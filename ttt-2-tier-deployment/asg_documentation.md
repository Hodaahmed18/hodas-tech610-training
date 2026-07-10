# Auto Scaling Group: Build, Test, and Teardown

## How it works

An Auto Scaling Group (ASG) automatically launches and terminates app instances based on demand, using a Launch Template as the blueprint for every new instance. It replaces "someone manually launching a VM" with "AWS launching VMs automatically according to rules."

*(Diagram from earlier today goes here: Internet -> Load Balancer -> ASG spanning two AZs, each running an App VM, fed by a Launch Template referencing the AMI + security group)*

## What a Load Balancer is, and why it's needed

A load balancer sits in front of the ASG and distributes incoming traffic across whichever instances are currently healthy and running. Without it, users would need to know the specific IP of one instance, which defeats the purpose of having multiple, since instances get added/removed automatically and their IPs change every time.

The load balancer also does health checks continuously, if an instance stops responding correctly, the load balancer stops sending it traffic even before the ASG replaces it.

## Steps to Build the ASG

1. **Create a Launch Template**
   - AMI: `hodastech610-tictactoe-ami` (`ami-0432c684d4302819d`)
   - Instance type: `t3.micro`
   - Security group: `hoda-tech610.sg`
   - User data (app-only, no DB connection):
     ```bash
     #!/bin/bash
     pm2 start /home/ubuntu/app/app/index.js
     ```

2. **Create the Auto Scaling Group**
   - Uses the Launch Template above
   - Group size: desired 2
   - Scaling: min 2, max 3
   - Scaling policy trigger: CPU 50%
   - Attach to a Load Balancer for traffic distribution across instances

3. **Test it's working**
   - Hit the Load Balancer's DNS/public address
   - Confirm the app loads (Local Scoreboard, since DB isn't connected for this task)

## How to Manage Instances

- EC2 → Auto Scaling Groups → select the group → **Instance management** tab shows every instance currently in the group, its health status, and which AZ it's in
- Instances can be manually set to Standby (removed from load balancing without being terminated) if you need to work on one without the ASG replacing it

## Creating a Healthy/Unhealthy Instance (for testing)

1. SSH into one of the running instances
2. Ran `sudo pm2 stop index` to stop the app process (note: process was running under root/sudo's pm2, not the ubuntu user's, so `sudo` was required to see and stop it)
3. Target group health check caught it within about a minute, status flow observed: 1 Healthy → 1 Draining + 1 Initial → back to 2 Healthy
4. Why it's marked unhealthy: the target group runs periodic HTTP health checks against each instance. Once the app process stopped responding, the health check began failing, flipping that instance to unhealthy/draining. The ASG automatically launched a replacement instance from the same launch template, which was health-checked and brought into rotation once healthy, restoring the group to full capacity without any manual intervention.

## SSH Access

```bash
ssh -i C:\Users\xirsi\.ssh\hodas-tech610.pem ubuntu@<instance-public-ip>
```
Same key used all week, get the instance's public IP from EC2 → Instances → select the specific ASG-launched instance.

## Deleting the ASG and All Connected Parts

Order matters, delete in this sequence:
1. **Delete the Auto Scaling Group** first (this terminates all instances in it automatically) — EC2 → Auto Scaling Groups → select → Delete
2. **Delete the Load Balancer** — EC2 → Load Balancers → select → Delete
3. **Delete the Target Group** — EC2 → Target Groups → select → Delete
4. **Delete the Launch Template** — EC2 → Launch Templates → select → Delete

Deleting in this order avoids dependency errors (you can't delete a Launch Template that's still referenced by an active ASG, for example).

## Screenshots

*(Insert 1-2 screenshots of the trickiest parts here, e.g. the healthy/unhealthy status flip, or the launch template user data field)*

## Extra: Database + Autoscaling Together (if time allows)

*(Only fill in if attempted)*

Only one DB VM is used, since the database itself isn't autoscaled, only the app tier is. The difference from earlier deployments: the app-side user data needs the `MONGODB_URI` and `STATEFUL_MODE` exports added back in, but the DB VM itself stays as a single fixed instance outside the ASG entirely.
