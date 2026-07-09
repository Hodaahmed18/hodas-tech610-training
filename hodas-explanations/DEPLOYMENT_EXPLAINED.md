# 🧠 Deployment Explained — The Full Picture

This document explains every step of the deployment process in plain English.
Not just what the commands DO — but WHY we're doing them, and what would happen if we didn't.

---

## 🌐 The Big Picture

We have a Node.js app (Tic Tac Toe) sitting on our laptop as a zip file.
We want it to be live on the internet so anyone can visit it in a browser.

To do that we need:
1. A server, basically a computer running in the cloud (AWS EC2)
2. The right software installed on that server
3. The app's code transferred onto it
4. The app actually running
5. A way for the internet to reach it cleanly

That's it. Everything below is just making those 5 things happen.

---

## ☁️ Step 1 : The EC2 Instance

When you create an EC2 instance, AWS gives it:

- A **private IP** (like 172.31.x.x) : used internally within AWS

- A **public IP** (like 108.130.114.248) : used by the outside world to reach it

**Why does this matter?**

The public IP is what you put in the browser. The private IP is what the server uses to talk to other AWS services internally.

---

## 🔒 Step 2 : Security Group

Before we can even connect to the server, we need to tell AWS what traffic to allow in.
A security group is basically a firewall, a list of rules that control who can knock on which door.

We opened three ports:
- **Port 22** :SSH. This is how we connect to and control the server remotely.
- **Port 3000** : where our Node.js app listens by default.
- **Port 80** : standard HTTP traffic. This is what browsers use when you visit a URL without a port number.

**Why not just open everything?**
Because every open port is a potential attack surface. We only open what we actually need.

**Why did we lock SSH to our own IP?**
Because if port 22 is open to the whole internet, anyone can try to brute-force their way in.
Locking it to your IP means only you can attempt to connect.

---

## 🔑 Step 3 SSH In

```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
``

- `YOUR_PUBLIC_IP` : the address of your server.

**Why a key file instead of a password?**
Key-based authentication is much harder to crack than a password.
The key file contains a long cryptographic string that can't be guessed.

---

## 📦 Step 4 : Update the System

```bash
sudo apt update -y && sudo apt upgrade -y
```
**Why do this first?**
A fresh server might have outdated packages with known security vulnerabilities.
Always update before installing anything.

---

## 🌐 Step 5 : Install nginx

```bash
sudo apt install nginx -y
```

nginx (pronounced "engine-x") is a web server.

Think of it as the front desk of a building.
When someone visits your server's IP in a browser, nginx is the first thing that receives that request.
It then decides where to send it.

Right now we're just installing it. We configure what it actually does in Step 9.

---

## 📂 Step 6 : Install unzip

```bash
sudo apt install unzip -y
```

The app arrives as a `.zip` file. Ubuntu doesn't have unzip installed by default.
This just adds the tool we need to extract it.

---

## 🟢 Step 7 : Install Node.js v20

This takes three commands and it's worth understanding why.

```bash
curl -sL https://deb.nodesource.com/setup_20.x -o nodesource_setup.sh
```

- `curl` : a tool for downloading files from the internet.
- `-sL` : silent (no progress spam) and follow redirects.
- `-o nodesource_setup.sh` : save it as a file called nodesource_setup.sh.

This downloads a setup script from NodeSource : the official source for Node.js packages.

**Why not just `apt install nodejs`?**
Because Ubuntu's default repository has an old version of Node.js.
We specifically need v20. This script tells apt "when I ask for nodejs, get it from NodeSource, and get v20."

```bash
sudo bash nodesource_setup.sh
```

This runs the script we just downloaded.
It configures the correct repository so the next command pulls the right version.

```bash
sudo apt install nodejs -y
```

Now we actually install Node.js v20.

---

## 📁 Step 8 : Transfer and Unzip the App

The app zip file needs to get from your laptop onto the server.
We use SCP (Secure Copy) it copies files over SSH.

Run this from your LOCAL machine, not from inside the SSH session:

```bash
scp -i your-key.pem your-app.zip ubuntu@YOUR_IP:/home/ubuntu/
```

- `scp` : secure copy
- `-i your-key.pem` : same key you use for SSH
- `your-app.zip` : the file on your laptop
- `ubuntu@YOUR_IP:/home/ubuntu/` : where to put it on the server

Then back on the server, unzip it:

```bash
unzip nodejs20-sparta-tictactoe-v1-2.zip
```

This creates an `app/` folder containing all the application code.

---

## 📦 Step 9 : Install App Dependencies

```bash
cd app
npm install
```
This tells nginx: "instead of looking for a file, pass this request to the app running on port 3000."

Then restart nginx to apply the change:

```bash
sudo systemctl restart nginx
```

---

## ⚙️ Step 10 : Configure nginx as a Reverse Proxy

This is the clever bit.

Right now the app runs on port 3000. To access it, users would have to type:
`http://YOUR_IP:3000`

That's ugly and non-standard. We want them to just type:
`http://YOUR_IP`

nginx can sit on port 80 (standard HTTP) and quietly forward all traffic to port 3000 internally.
The user never sees port 3000. This is called a **reverse proxy**.

We edit nginx's config file to make this happen:

```bash
sudo sed -i 's|try_files $uri $uri/ =404;|proxy_pass http://localhost:3000;|g' /etc/nginx/sites-available/default
```

- `sed` — Stream Editor. Finds and replaces text in a file.
- `-i` — edit the file in place (saves the change).
- `s|old text|new text|g` — substitute old with new.
- We use `|` instead of `/` because the text itself contains `/` characters.


We're replacing:  try_files $uri $uri/ =404;

With:    proxy_pass http://localhost:3000;

This tells nginx: "instead of looking for a file, pass this request to the app running on port 3000."

Then restart nginx to apply the change:

```bash
sudo systemctl restart nginx
```

---

## 🚀 Step 11 : Start the App with pm2

```bash
sudo npm install -g pm2
pm2 start index.js
```

If we just run `npm start`, the app runs in the foreground.
The moment you close your terminal or disconnect, the app dies.

pm2 is a process manager, it runs the app in the background and keeps it alive even after you disconnect.
It also automatically restarts the app if it crashes.

- `npm install -g pm2` : install pm2 globally so it's available anywhere
- `pm2 start index.js` : start the app and hand it off to pm2 to manage

---

## ✅ The End Result

Visit `http://YOUR_IP` in a browser.

nginx receives the request on port 80.
It passes it to the app running on port 3000.
The app responds.
You see Tic Tac Toe.

The whole journey:

Browser → Port 80 → nginx → Port 3000 → Node.js app → Response

OKAY NOW FOR THE WHY

---

## 🤖 Why Automate It?

Doing this manually once teaches you what's happening.
But in the real world you might need to deploy the same app to 10 servers,
or redeploy every time there's an update.

A bash script runs every step automatically, in order, without human error.
That's what `deploy.sh` does : it's the entire process above in one file.

---

## 🔄 What Would Change for a Different App?

If you deployed a different Node.js app, most of the script stays the same:
- System update ✅ same
- nginx install ✅ same
- Node.js install ✅ same
- nginx reverse proxy config ✅ same
- pm2 ✅ same

What would change:
- The zip file name
- The entry point (`index.js` might be `app.js` or `server.js`)
- The port number (if not 3000)
- Any app-specific environment variables

That's the power of automation : the infrastructure is reusable,
only the app-specific parts need changing.
