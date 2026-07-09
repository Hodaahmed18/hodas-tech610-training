# Flask Weather API Deployment — Explained

This document explains every decision made during the deployment.
Not just what we ran, but why we ran it and what would break without it.

---

## The Big Picture

We have a Python Flask API sitting on a server.
It takes a UK postcode, converts it to coordinates, and returns live weather data.

To make it publicly accessible we need:
1. A server in the cloud
2. The right software installed
3. The app running and staying alive
4. A way for the internet to reach it cleanly

Same pattern as every deployment. Only the tools change based on the language.

---

## Why This Is Different From the Node.js Deployment

The tictactoe app was JavaScript. This is Python.
Different language means different tools — but the infrastructure pattern is identical.

The only things that changed:
- pip3 instead of npm (different package manager, same job)
- gunicorn instead of npm start (different server, same job)
- Port 5000 instead of 3000 (Flask default instead of Node default)

Everything else — nginx, pm2, EC2, security groups, sed — stayed exactly the same.

---

## Step 1 — EC2 Instance

Fresh Ubuntu 26.04, t3.micro on AWS.

Security group rules:
- Port 22: SSH, locked to your IP only
- Port 80: HTTP, open to everyone
- Port 5000: app port, open to everyone

Port 5000 needs to be open because Flask runs there by default.
Port 80 is where nginx listens, it's the public-facing entry point.

---

## Step 2 — System Update

```bash
sudo apt update -y && sudo apt upgrade -y
```

Always do this first on a fresh instance.
Outdated packages mean outdated security vulnerabilities.

---

## Step 3 — Install nginx

```bash
sudo apt install nginx -y
```

nginx is the front door. It listens on port 80 and forwards traffic
to the app internally. The user never sees port 5000.

Same role as in the Node deployment. Nothing changed here.

---

## Step 4 — Install Python Dependencies

```bash
sudo apt install python3-pip -y
pip3 install flask requests gunicorn --break-system-packages
```

pip3 is Python's package manager. Same concept as npm, it reads a
dependency list and installs everything the app needs.

Three things installed:
- flask: the web framework the app is built on
- requests: lets Python make HTTP calls to external APIs
- gunicorn: the production server that runs Flask properly

--break-system-packages is needed on newer Ubuntu versions because
pip and the system package manager would conflict otherwise.

---

## Step 5 — Transfer Files

The app needs two files on the server:
- weather_api.py: the application code
- weather_api_key: the OpenWeatherMap API key



```bash
scp -i your-key.pem weather_api.py ubuntu@YOUR_IP:/home/ubuntu/
scp -i your-key.pem weather_api_key ubuntu@YOUR_IP:/home/ubuntu/
```
SCP runs from your local machine, not from inside SSH.

---

## Step 6 — Why Gunicorn

Flask has a built-in server you can run with python3 weather_api.py.
It works but Flask itself warns you not to use it in production.

Reasons:

- Can only handle one request at a time
- Not designed for stability under real traffic
- Debug mode left on by default is a security risk

Gunicorn replaces it. It handles multiple requests, is stable, and
is the standard way to run Flask in production.

```bash
gunicorn --bind 0.0.0.0:5000 weather_api:app
```

- 0.0.0.0: listen on all network interfaces, not just localhost
- 5000: the port Flask defaults to
- weather_api:app: the filename and the Flask app object inside it

---

## Step 7 — nginx as Reverse Proxy

Same as tictactoe. One sed command edits the nginx config automatically:

```bash
sudo sed -i 's|try_files $uri $uri/ =404;|proxy_pass http://localhost:5000;|g' \
/etc/nginx/sites-available/default
sudo systemctl restart nginx
```

This tells nginx: anything hitting port 80, forward it to port 5000.
User types the IP, hits port 80, nginx silently passes it to the app.

---

## Step 8 — pm2 to Keep It Alive

Gunicorn blocks the terminal. Close the terminal and the app dies.
pm2 solves this the same way it did for Node.

```bash
pm2 start "gunicorn --bind 0.0.0.0:5000 weather_api:app" --name weather-api
```

pm2 doesn't care what language the process is. It just keeps it running.

---

## Step 9 — Test

http://YOUR_IP/weather?postcode=SW1A1AA

nginx receives it on port 80, passes it to gunicorn on port 5000,
gunicorn runs the Flask app, Flask calls the postcode and weather APIs,
returns JSON.

---

## What I Learned

The deployment pattern is reusable. Language doesn't change the infrastructure.

As a DevOps engineer you need to know:
- What runtime does the app need
- What installs its dependencies
- What command starts it
- What port it runs on

The code inside the app is the developer's responsibility.
Getting it running, keeping it running, and making it reachable is yours.

---

## THE Key Differences Summary

| | Node.js (Tictactoe) | Python (Flask API) |
|---|---|---|
| Package manager | npm | pip3 |
| Server | npm start | gunicorn |
| Port | 3000 | 5000 |
| Process manager | pm2 | pm2 |
| Reverse proxy | nginx | nginx |
| Transfer method | scp zip file | scp individual files |
