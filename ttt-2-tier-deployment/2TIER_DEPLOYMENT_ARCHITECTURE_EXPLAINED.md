# 2-Tier Deployment and Architecture, Explained

## What "tiers" actually means

A tier is a physically separate machine doing one job. Splitting an application into tiers means each piece of functionality lives on its own instance, rather than everything running on a single box.

**The progression:**

1. **Monolith** — one machine does everything: app logic, database, web server, all on the same box
2. **2-tier** — the application is split into two machines: an app tier and a database tier
3. **3-tier** — a third layer is added, usually a presentation/frontend layer separate from the app logic layer
4. **Microservices** — instead of splitting by technical layer, the application is split by business capability, each service owns one specific piece of functionality (e.g. a payments service, a user-auth service, a notifications service), each with its own deployment, scaling, and often its own database

**N-tier vs microservices, the real distinction:** N-tier splits by technical layer (presentation, logic, data). Microservices splits by business capability. It is not simply "more pieces", it is a different axis of separation entirely.

## Why bother splitting into tiers at all

**Independent scaling.** If the app is getting hammered with traffic but the database is fine, you can add more app VMs without touching the database at all. In a monolith, you would have to scale the whole thing together even though only one part actually needs it.

**Fault isolation.** If the app crashes, the database's data is not affected, it is a separate machine. If the database needs maintenance, the app tier does not need to go down with it (assuming a graceful failure mode).

**Security.** The database can be locked away in a private subnet, unreachable from the internet, while only the app tier (which genuinely needs to be public) is exposed. A monolith has no way to selectively expose only part of itself.

**Separation of concerns.** Each machine has one job. Debugging is more direct because you know which tier a problem is likely to sit in, rather than untangling one box doing five jobs at once.

## The deployment ladder: getting an app running, with progressively less manual work

This is the full progression actually built and worked through, from most manual to most automated:

**Stage 1: Manual**
- SSH into the instance
- Type every command by hand: install dependencies, configure the app, start it
- Slowest, most error-prone, but the only way to genuinely understand what each step is doing before automating it away

**Stage 2: Bash scripting**
- The same commands from Stage 1, written into a single script (e.g. `prov-db.sh`, `deploy.sh`)
- Still requires SSHing in to run the script, but removes the risk of mistyping or forgetting a step
- This is where most real bugs actually surface and get fixed, since the script forces every step to be explicit

**Stage 3: User data**
- AWS runs a script automatically the moment an instance boots for the first time, no SSH required at all
- Critical gotcha: user data only runs on the instance's very first boot. It does not re-run on every restart. If an instance is stopped and started again, whatever user data set up (like starting a process with pm2) will not happen again, since that box has already had its "first boot"
- A second critical gotcha: user data is not an interactive shell. Anything relying on `.bashrc` being sourced will silently fail, since `.bashrc` only loads in interactive sessions, not automated boot scripts. Any environment variables an app needs must be exported directly in the user data script, immediately before the command that needs them

**Stage 4: AMI (Amazon Machine Image)**
- Take a snapshot of a fully configured, already-working instance
- Launch new instances directly from that image, with zero setup needed at boot
- An AMI is a snapshot of exactly whatever state the instance was in at the moment the image was created, nothing more, nothing less. If a required service was not yet running when the image was taken, it will never be running on any instance launched from that AMI
- Fastest and most production-like pattern is combining Stage 4 with a small amount of Stage 3: the AMI has the app/database baked in, and a short user data script just supplies environment variables and starts the process

## The 2-tier architecture, concretely

```
                Internet
                   |
            Internet Gateway
                   |
          Public Route Table
        (0.0.0.0/0 -> IGW route)
                   |
            Public Subnet
                   |
                App VM
        (runs the application code,
         reachable from outside)
                   |
        internal request over
        private IP, default route
        table, VPC-local traffic only
                   |
            Private Subnet
                   |
                DB VM
        (runs the database,
         no route to the internet,
         unreachable from outside)
```

**App tier**
- Runs the application code (in this case, a Node.js app managed by pm2, served through nginx as a reverse proxy)
- Lives in the public subnet, since it genuinely needs to be reachable by users
- Connects to the database over its private IP, never over the internet, even though both machines are technically in the same account

**Database tier**
- Runs the database itself (MongoDB in this build)
- Lives in the private subnet, with no route to the internet
- Only reachable from other instances inside the same VPC, and only on the specific port the database needs (27017 for MongoDB), enforced further by the security group

**How the app finds the database:** environment variables. The app checks for a connection string (`MONGODB_URI`, pointing at the database's private IP and port) and a mode flag (`STATEFUL_MODE=server`) confirming it should actually use that database rather than falling back to local-only storage. Both must be set correctly, or the app silently defaults to a local-only mode with no persistent data, and it does not tell you this happened, it just quietly behaves as if the database were never configured.

## Real bugs that came up building this, and what they taught

**Dead domain in a GPG key import.** A package repository's signing key was being pulled from a domain that no longer resolved to the actual key content, it silently returned an unrelated webpage instead of a real key file. The install then failed further downstream with a vague "package not found" error, since the real cause (a bad key) was several steps removed from where the failure actually surfaced.

**Version mismatch between a repository's declared suite and its pinned package versions.** A repository config pointed at one version number while the actual packages being installed were pinned to a slightly different one, causing apt to be unable to resolve what to install. The fix was matching the suite number to the actual pin.

**Double-sudo stripping environment variables.** Running `sudo` a second time while already inside a root shell (`sudo -i`) resets the environment by default, silently discarding any variables that had just been exported. This caused a duplicate process to spin up instead of the intended one, since the app started without the variables it needed and fell back to a default mode.

**Copying the wrong private IP.** Private IPs are unique per instance. Copying a value intended for a different machine's environment variables points the app at someone else's database, or at nothing at all. Always confirm the actual private IP of the specific instance being connected to, not a value copied from a shared example or a different session.

**Environment variables written into `.bashrc` inside user data.** As above, `.bashrc` never sources during a non-interactive boot script, so anything relying on it appears to succeed at the "export" step but never actually takes effect once the app tries to start.

**User data left empty or a launch skipped it entirely.** Results in a 502 Bad Gateway. The reverse proxy (nginx) is a properly installed service and starts fine, but there is nothing behind it to proxy to, since the process that should have started never received its start instruction. Restarting the instance does not fix this either, since user data does not re-run on restart, only on first boot.

**Hardcoding values before taking a snapshot.** If environment variables are set manually on an instance and then that instance is used to create an AMI, those values get baked permanently into every future instance launched from that image, independent of whatever user data is (or isn't) provided at launch time. This can look like a working automated setup when it is actually values frozen from one specific moment, not a repeatable process.

## Why this matters beyond the course

At real companies, the manual/scripted versions of everything above get replaced by tools that do the same job at scale:

- **Infrastructure as Code** (Terraform) replaces manually building VPCs, subnets, and instances by hand, the whole environment gets defined in code and can be recreated identically anywhere
- **CI/CD pipelines** replace manually running deployment scripts, code changes trigger automated build, test, and deploy steps
- **Containers and Kubernetes** replace AMI-based deployment for many workloads, offering faster, more portable packaging than a full VM image
- **Managed database services** (RDS, MongoDB Atlas) replace self-hosting and manually securing a database VM, the provider handles patching, backups, and much of the security hardening
- **Dedicated monitoring stacks** (Datadog, Prometheus, PagerDuty) replace manually wiring up CloudWatch alarms and SNS topics by hand

The course teaches the manual version first specifically because it is difficult to appreciate what any of these tools are actually abstracting away until the manual pain point has been genuinely felt firsthand.
