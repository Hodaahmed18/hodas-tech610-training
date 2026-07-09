# Week 4 Friday: Everything Explained (Confused Edition)i
## From "What Even Is A Server" to AMIs in One Document

---

## Firstly: What Even Is A Server?

A server is just a computer. That's it.

The difference between your laptop and a server:
- Your laptop is for you personally
- A server is designed to be always on, always connected, and to handle requests from other people

An **EC2 instance** (Elastic Compute Cloud) is just AWS renting you one of their computers in a data centre somewhere. You configure it, you connect to it, you run stuff on it.

---

## What Is An IP Address?

Every device connected to the internet has an address, like a house number.

- **Private IP** (e.g. 172.31.x.x): only reachable inside AWS's private network. Other servers can talk to it, but the public internet cannot.
- **Public IP** (e.g. 34.244.60.80): the address anyone on the internet can reach. This is what you put in your browser to verify the app is running.

When your instance stops and starts, the public IP changes. That's why your SSH command breaks after a reboot.

---

## What Is A Port?

If an IP address is the building, a port is the door into a specific room.

- **Port 22**: SSH (how you remotely control the server)
- **Port 80**: standard HTTP web traffic (what browsers use by default)
- **Port 3000**: where the Node.js app (TicTacToe) listens
- **Port 5000**: where the Flask (Python) app listens

When you type `http://34.244.60.80` with no port number, your browser automatically uses port 80. That is exactly why we configure nginx: so when someone types just the IP address, nginx catches it on port 80 and redirects it to wherever our app actually lives.

---

## What Is A Security Group?

A virtual firewall. A list of rules that control what traffic can reach your server.

Examples:
- "Allow SSH on port 22 from my IP only" (so only you can log in)
- "Allow HTTP on port 80 from anywhere" (so anyone can visit the app)

Without a security group rule, traffic is blocked by default.

---

## What Is SSH?

SSH (Secure Shell) is how you remotely control a Linux server from your terminal.

Instead of sitting physically at the server, you open a terminal on your laptop and type:

```bash
ssh -i your-key.pem ubuntu@PUBLIC_IP
```

- `-i your-key.pem`: your key file. Proves you are who you say you are. Like a digital ID card.
- `ubuntu@`: the username on the server. Ubuntu instances use `ubuntu`.
- `PUBLIC_IP`: the address of your server.

Once connected, everything you type runs on the remote server, not your laptop.

---

## How To Launch An EC2 Instance (Step By Step)

1. Go to **AWS Console** → search **EC2** → click **Instances** → **Launch Instance**
2. **Name**: give it something meaningful e.g. `hoda-tictactoe`
3. **AMI** (Amazon Machine Image): choose **Ubuntu Server 26.04 LTS**. This is the operating system.
4. **Instance type**: choose **t3.micro** (free tier, small, enough for learning)
5. **Key pair**: select your key pair. This is the file that lets you SSH in.
6. **Security group**: select an existing one if already configured, or create one with:
   - Port 22, source: My IP
   - Port 80, source: Anywhere
   - Port 3000 or 5000, source: Anywhere
7. **User data**: paste your bash script here if you want it to run on startup
8. Click **Launch instance**
9. Wait about 1 minute for it to reach "Running" state
10. Copy the **Public IPv4 address**: that's your server's address

---

## The Progression: Every Stage Explained

### Stage 1: Manual Deployment

You SSH into a blank server. You type every command yourself.

```bash
sudo apt update -y
sudo apt install nginx -y
curl -sL https://deb.nodesource.com/setup_20.x -o nodesource_setup.sh
sudo bash nodesource_setup.sh
sudo apt install nodejs -y
git clone https://github.com/repo app
cd app
npm install
pm2 start index.js
```

**The problem:** You have to do this every single time for every new server. One typo and it breaks.

---

### Stage 2: Bash Script 

Same commands, but now written in a file as a script.

```bash
#!/bin/bash
# The #!/bin/bash line (called a shebang) tells the system:
# "run this file using bash, the Linux command language"

sudo apt update -y &>/dev/null
# &>/dev/null silences the output so you don't get walls of text
# errors still show if something actually breaks

echo "Installing nginx..."
sudo apt install nginx -y &>/dev/null
```

You write it once. You SCP (Secure Copy) it to the server. You run it once.

**What improved:** No more typing commands manually. Same script, same result every time.

**What's still annoying:** You still have to SSH in first and manually trigger it.

---

### Stage 3: User Data

AWS lets you paste your bash script into the instance setup wizard BEFORE it launches.

When the server boots for the first time, AWS runs your script automatically. No SSH needed at all.

**Where to find it:**
Launch Instance → scroll down to **Advanced Details** → **User data** field → paste your script

```bash
#!/bin/bash
# This runs automatically when the instance first boots
# Crucially: it runs as ROOT, not as ubuntu
sudo apt update -y
```

**What improved:** Zero human intervention after clicking Launch. Server configures itself.

---

### The Problem With User Data: Two Attempts at TicTacToe

We actually ran this exercise twice today and hit real problems. Both worth understanding.

**Attempt 1: User Data Only (Full Script)**

The script ran on boot and installed everything. But people kept getting Bad Gateway or permission errors.

Why:

User data runs as **root** (the system administrator account). Root creates the app folder. Root owns it.

When the script then tries to run `npm install`, it's writing files into a folder owned by root. On some systems this causes permission conflicts.

```
npm error: EACCES: permission denied
```

Bad Gateway appeared because nginx was running but the app wasn't. Either npm install failed silently (hidden by `&>/dev/null`) or pm2 couldn't start properly.

**The fix:**

```bash
chown -R ubuntu:ubuntu /home/ubuntu/app
# chown = change owner
# -R = recursively (all files inside too)
# ubuntu:ubuntu = new owner : new group
# /home/ubuntu/app = the folder to fix   (my approach, but removes root from accessing so maybe don't)
```

Or run the problematic commands explicitly as the ubuntu user:

```bash
sudo -u ubuntu npm install
# sudo -u ubuntu = run this as ubuntu even though we are currently root
sudo -u ubuntu pm2 start index.js
```

**Attempt 2: AMI + Minimal User Data**

After getting the app working manually on one instance, we took a snapshot of it (an AMI) and launched a new instance from that.

User data this time was just:

```bash
#!/bin/bash
cd /home/ubuntu/app/app
pm2 start index.js
```

Three lines. No installs. No permission issues. App up in seconds.

That's the point. The AMI already had everything installed. User data just needed to press play.

---

### Stage 4: AMI (Amazon Machine Image)

An AMI is a complete snapshot of a running server. It captures:
- The operating system
- Every piece of software installed (Node, nginx, pm2, etc)
- All configuration files
- The app code

When you launch a new instance from an AMI, it comes up already configured. No installation. No waiting.

Think of it like this:
- Instance: a cake
- AMI: the recipe AND a photo of the finished cake
- New instance from AMI: baking an identical cake in 30 seconds instead of 30 minutes

**How to create an AMI from a running instance:**

1. Go to **EC2 → Instances**
2. Select your running instance
3. Click **Actions → Image and templates → Create image**
4. Give it a name e.g. `hoda-tictactoe-ami`
5. Leave everything else default
6. Click **Create image**
7. Go to **EC2 → AMIs** in the left sidebar: wait for status to change from `Pending` to `Available`

**How to launch an instance FROM an AMI:**

1. Go to **EC2 → AMIs**
2. Select your AMI
3. Click **Launch instance from AMI**
4. Choose t3.micro
5. Choose your key pair
6. Choose your security group
7. Add minimal user data to start the app
8. Launch

**What improved:** New instances launch in seconds. Perfect copy every time.

**One catch:** pm2 processes do not survive a snapshot. The software is there but the app is not running. That is what the minimal user data handles.

---

### Stage 5: AMI + User Data (The Final Form)

- **AMI** handles the heavy lifting: OS, Node, nginx, all pre-installed
- **User data** handles the lightweight bit: just start the app

```bash
#!/bin/bash
cd /home/ubuntu/app/app
pm2 start index.js
```

**Why this is powerful:**
- Launches in seconds
- App starts automatically
- Zero human involvement
- Need 100 servers? Same process, 100 times, automated

---

## Environment Variables: Why They Matter

You have an API key. A secret. Something your app needs but should not behardcoded.

**Best: environment variable**

```bash
export WEATHER_API_KEY=your_key_here
# export = make this variable available to child processes like Python
```

**Making it permanent (survives closing the terminal):**

```bash
echo "export WEATHER_API_KEY=your_key" >> ~/.bashrc
# >> = APPEND to the file, not overwrite
# ~/.bashrc = a file that runs every time a terminal opens
source ~/.bashrc
# source = reload the file immediately without restarting
```

**`>` vs `>>`:**
- `>`: overwrites the file completely
- `>>`: adds to the end of the file

---

## nginx: What It Actually Does

nginx (pronounced "engine-x") is a web server.

Without nginx, your app runs on port 3000. Users have to type:
`http://34.244.60.80:3000`

With nginx as a reverse proxy:
- nginx listens on port 80 (default web port)
- Someone visits your IP, nginx catches it on port 80
- nginx silently forwards it to your app on port 3000
- User just types `http://34.244.60.80` and it works

The config change (done automatically with `sed`):

```bash
sudo sed -i 's|try_files $uri $uri/ =404;|proxy_pass http://localhost:3000;|g' /etc/nginx/sites-available/default
# sed = stream editor
# -i = edit the file in place (saves the change)
# s|old|new|g = substitute old text with new text
sudo systemctl restart nginx
# restart nginx so it picks up the config change
```

---

## pm2: Why Not Just npm start?

`npm start` runs your app in the foreground. Close the terminal and the app dies.

pm2 is a process manager. It runs your app in the background and keeps it alive.

```bash
pm2 start index.js    # start the app, hand it to pm2
pm2 status            # see what's running
pm2 restart index     # restart the app
pm2 kill              # stop everything
```

pm2 also auto-restarts if the app crashes. That is production-grade behaviour.

---

## (David's List, But With Context)

### 1. Manual Deployment

You SSH into a blank server. You type every command yourself.

```bash
sudo apt update
sudo apt install nginx
sudo apt install nodejs
npm install
npm start
```

Every. Single. Time. For every server.

**What's wrong with this:**
- You have to do it again for every new server
- You'll probably make a typo
- Nobody else knows how to replicate what you did
- If the server dies, you start from scratch

---

### 2. Bash Script

Same commands but now you put them in a file referred to as a script

```bash
#!/bin/bash
sudo apt update -y
sudo apt install nginx -y
# etc
```

You write it once. You run it whenever you need it.

**What improved:**
- No more typing commands manually
- Reproducible. same script, same result every time
- Can share it with your team

**What's still annoying:**
- You still have to SSH into the server first
- You still have to SCP the script across
- Still requires a human to be involved

---

### 3. User Data

AWS lets you paste your script into the instance setup wizard BEFORE it launches.

When the server boots for the first time, AWS runs your script automatically. No SSH. No manual trigger. The server configures itself.

**What improved:**
- Zero human intervention after clicking Launch
- Server installs everything and starts the app on its own
- You just wait, then hit the IP in a browser

**What's still annoying:**
- Every new instance still has to run through the whole install process
- Installing Node.js, nginx, npm packages, this takes 5-10 minutes every time
- If you need 10 servers, each one sits there installing for 10 minutes

---

### 4. AMI (Amazon Machine Image)

You take a fully configured, working instance and snapshot it.

That snapshot captures:
- The operating system
- Every piece of software you installed
- All your configuration files
- The app code

Now when you launch a new instance from that AMI, it comes up already installed. No setup. No waiting.

**What improved:**
- New instances launch in seconds instead of minutes
- No installation step at all, everything is already there
- Perfect copy of a working server, every time

**One catch:**
The app itself might not be running yet. The AMI captured the state of the server, but pm2 processes don't survive a snapshot. You still need to start the app.

---

### 5. AMI + User Data (The Best of Both)

This is the final form.

- AMI handles the heavy stuff: OS, Node, nginx, all pre-installed
- User data handles the lightweight stuff: just start the app

```bash
#!/bin/bash
cd /home/ubuntu/app/app
pm2 start index.js
```

That's it. That's your entire user data script when you're launching from an AMI.

**Why this is powerful:**
- Launches in seconds (AMI)
- App starts automatically (user data)
- Zero human involvement
- Infinitely repeatable
- Scale to 100 servers? Same process, 100 times, automated



---

## How All Today's Exercises Connect

```
            Manually typed commands into a server to familiarise
                                ↓
            Wrote bash scripts: same commands, automated, reusable
                                ↓
   Pasted bash scripts into User Data: AWS runs it on boot, no SSH needed
                                ↓
                  Hit real problems with User Data:
                 - Script runs as root, not as ubuntu
            - Files created by root cause permission errors for ubuntu
                - npm install failed silently, pm2 couldn't start
           - Result: Bad Gateway — nginx running but app not found
           - Fix: chown -R ubuntu:ubuntu or sudo -u ubuntu for installs
                                ↓
            Realised User Data alone is fragile for complex setups
                                ↓
          Created AMI from a fully working, manually fixed instance
        - AMI snapshots everything: OS, Node, nginx, config, app code
           - But does NOT snapshot running processes
                 (pm2 dies with the snapshot)
                                ↓
                     Launched new instance from AMI
            - Heavy lifting already done: no installs, no setup
              - But app not running: pm2 didn't carry over
           - Needed minimal user data just to start the app:
                           #!/bin/bash
                        cd /home/ubuntu/app
                          pm2 start index.js
                                ↓    
               AMI + minimal User Data: the final form
                - AMI handles everything pre-installed
     - User data handles what can't be baked in: starting live processes
            - Result: fastest, most automated, most scalable
```

Each step basically removed one more manual action. 

---

## Common Questions That Actually Came Up Today

**Q: Why did some people get Bad Gateway?**
A: nginx was running but couldn't reach the app on port 3000. Either the app wasn't started, or npm install failed silently because of the root permissions issue. nginx said "I'm here but nobody's home."

**Q: Why does user data run as root?**
A: AWS designed it that way. Root has permission to do everything on a fresh system. The downside is files it creates are owned by root, which causes permission issues for the ubuntu user later.

**Q: Why create an AMI from a working instance?**
A: Because you have already done the hard work of installing everything. The AMI saves that state. Future instances skip all the installation and start immediately.

**Q: Why do I need user data when launching from an AMI?**
A: The AMI saves installed software but not running processes. pm2 was running on the original instance, but a snapshot does not capture "things that are running". You need to start the app again. One line of user data does it.

**Q: Why port 80 and not just port 3000?**
A: Browsers default to port 80. Nobody wants to type :3000 in a URL. nginx bridges the gap.

---

## Concept Summary

We went from typing every command manually into a server, to having AWS automatically boot a pre-configured server with our app already running. And every exercise this week was just removing one more manual step at a time.
