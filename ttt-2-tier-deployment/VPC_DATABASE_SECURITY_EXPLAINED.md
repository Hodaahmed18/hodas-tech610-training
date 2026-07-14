# VPC and Database Security

## What is a VPC and why build a custom one

A VPC (Virtual Private Cloud) is an isolated network inside AWS. Every AWS account gets a default VPC per region, with default subnets already set up, but that default VPC is shared logically across everyone using the account. On the Sparta shared account, that means relying on the default VPC would mean sharing network space with the rest of the cohort.

Building a custom VPC gives full control over:
- The IP address range (no clashes with anyone else's setup)
- The subnet split, which parts are public and which are private (default VPC subnets are all public, no choice)
- Route tables and gateways, not shared or inherited from a default someone else can also touch

This is also the real-world reason companies build their own VPCs: to keep one team's environment isolated from another's, and to make sure a database is never exposed to the internet by accident.

## How this links to database security

A private subnet is a genuine network-level security control, not just a naming convention. A private subnet has no route out to the internet at all. Even if someone had the database's private IP and the security group allowed the port, there is no path in from outside AWS. This is a wall at the network layer, sitting in front of the security group (which works at the instance layer).

The two layers together:
1. Network layer: private subnet has no route to the internet gateway, so nothing outside the VPC can reach it
2. Instance layer: security group only allows traffic on port 27017 from within the VPC's own CIDR range, not from anywhere

## Architecture

```
Internet (HTTP)
      |
Internet Gateway
      |
Public Route Table (0.0.0.0/0 -> IGW, 10.0.0.0/16 -> local)
      |
Public Subnet (10.0.2.0/24)
      |
   App VM (SG: allows 22, 80)
      |
      | (internal request, via default route table, 10.0.0.0/16 -> local)
      v
Private Subnet (10.0.3.0/24)
      |
   DB VM (SG: allows 22, 27017 from 10.0.0.0/16 only)
```

The private subnet stays on the VPC's default route table, which only contains the local route. No custom route table, no internet gateway route is ever attached to it.

## Build steps

1. **Create VPC**
   - CIDR block: `10.0.0.0/16`
   - Resource type: VPC only

2. **Create subnets**
   - Public subnet: `10.0.2.0/24`, Availability Zone `eu-west-1a`
   - Private subnet: `10.0.3.0/24`, Availability Zone `eu-west-1b`
   - Note: both subnets must be in different AZs for genuine high availability. First attempt at this build put both subnets in the same AZ by mistake, see Bugs section below.

3. **Create and attach an Internet Gateway**
   - Create the IGW as its own resource
   - Attach it to the VPC (this step is separate from creation)

4. **Create a custom route table for the public subnet**
   - Add route: `0.0.0.0/0 -> Internet Gateway`
   - The `10.0.0.0/16 -> local` route already exists by default on every new route table
   - Associate this route table with the public subnet only

5. **Leave the private subnet on the VPC's default route table**
   - No changes needed here. This is what AWS creates automatically the moment the VPC is created, and it only ever contains the local route unless something is deliberately added to it.

6. **Create a new security group for this VPC**
   - Security groups are scoped to a single VPC, so a new VPC always needs its own SG, even if the rules mirror an existing one
   - DB VM SG: allow port 22 (SSH), allow port 27017 (MongoDB) with source set to `10.0.0.0/16`, not `0.0.0.0/0`
   - App VM SG: allow port 22 (SSH), allow port 80 (HTTP) with source `0.0.0.0/0`

7. **Launch the DB VM**
   - Into the private subnet
   - Using the existing MongoDB AMI, no user data required since MongoDB is already baked in
   - Note the private IP once running

8. **Launch the App VM**
   - Into the public subnet
   - Using the tictactoe AMI
   - User data:
     ```bash
     #!/bin/bash
     export MONGODB_URI=mongodb://<DB_PRIVATE_IP>:27017/tictactoe
     export STATEFUL_MODE=server
     pm2 start /home/ubuntu/app/app/index.js
     ```

9. **Confirm working**
   - Visit the App VM's public IP in a browser
   - Should show "Global Scoreboard" and "Mode: Persistent with Mongo DB"

## Bugs encountered

**Both subnets placed in the same Availability Zone.** On the first attempt, both the public and private subnet were created in `eu-west-1a`. This does not break app-to-database connectivity, since that only depends on the local route inside the VPC, not on AZ placement. It does remove the resilience benefit of spreading resources across separate physical data centers, meaning a failure in that one AZ would take down both tiers at once instead of just one. Fixed on the next build by placing the private subnet in `eu-west-1b`.

**App VM launched without user data.** On the first App VM launch, the user data field was left empty, resulting in a 502 Bad Gateway. This is the same failure mode as instances from a previous automation task: nginx starts because it is a genuinely installed service, but pm2 never runs since the instruction to start it only lives in user data, which only executes on first boot. Fixed by terminating and relaunching with the user data script correctly included.

## Cleanup

The first, code-along version of this VPC (including its IGW, route table, and security group) was deleted after the session, since it was only built to prove the pattern before the solo re-build. Deleting a VPC in AWS cascades to its dependent resources automatically, removing the internet gateway, route tables, and security groups tied to it, provided no instances are still running inside it. Both VMs were terminated first to avoid orphaned resources.
