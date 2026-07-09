# Flask Weather API — Cloud Deployment

## What This Is

A Python Flask API that takes a UK postcode, converts it to coordinates
via the Postcodes.io API, then fetches live weather from OpenWeatherMap.
Deployed on a fresh Ubuntu EC2 instance on AWS.

---

## The Big Picture

Same deployment pattern as a Node.js app just a different language,
different tools. The infrastructure is identical. Only the app-specific
parts change.

---

## How It Differs From Deploying a Node.js App

| Step | Node.js (Tictactoe) | Python (Flask API) |
|------|--------------------|--------------------|
| Language | JavaScript | Python |
| Package manager | npm | pip3 |
| Dependencies file | package.json | requirements.txt |
| Install command | npm install | pip3 install flask requests gunicorn |
| Server | npm start | gunicorn |
| Process manager | pm2 | pm2 (same) |
| Web server | nginx (same) | nginx (same) |
| Default port | 3000 | 5000 |

**What stayed the same:**
- Ubuntu EC2 instance
- Security group setup (SSH, HTTP, app port)
- nginx as reverse proxy
- pm2 to keep the app alive
- sed to automate nginx config

**What changed:**
- Python instead of Node.js
- pip3 instead of npm
- gunicorn instead of npm start
- Port 5000 instead of 3000
- Cloned from GitHub instead of transferring a zip

---

## Why These Tools

**pip3** : Python's package manager. Installs Flask, requests, gunicorn.
Same job as npm but for Python.

**gunicorn** : A production-grade Python WSGI server. Flask has a
built-in server but it's not safe for production — single-threaded,
not secure. Gunicorn handles multiple requests properly.

**pm2** : Same as Node deployment. Keeps gunicorn running headlessly
after you disconnect from SSH.

**nginx** : Same as Node deployment. Sits on port 80, forwards traffic
to the app on port 5000. User never sees the port number.

---

## Key Insight — DevOps vs Developer

As a DevOps engineer, the language inside the app is not your concern.
Whether it's JavaScript, Python, or Go we deploy it, we don't write it.

What you need to know:
- What runtime does it need? (Node, Python, etc)
- What command installs its dependencies? (npm, pip)
- What command starts it? (npm start, gunicorn)
- What port does it run on?

Everything else is the developer's concern.

---

## Deployment Steps

### 1. Launch EC2 Instance
- Ubuntu 24.04, t3.micro
- Security group: port 22 (SSH, your IP), port 80 (HTTP), port 5000

### 2. SSH In
```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
```

### 3. Update System
```bash
sudo apt update -y && sudo apt upgrade -y
```

### 4. Install nginx
```bash
sudo apt install nginx -y
```

### 5. Install Python and Dependencies
```bash
sudo apt install python3-pip -y
pip3 install flask requests gunicorn --break-system-packages
```

### 6. Transfer Files
From your local machine:
```bash
scp -i your-key.pem weather_api.py ubuntu@YOUR_IP:/home/ubuntu/
scp -i your-key.pem weather_api_key ubuntu@YOUR_IP:/home/ubuntu/
```

Note: the API key file must NOT be in GitHub. Transfer it separately.

### 7. Configure nginx as Reverse Proxy
```bash
sudo sed -i 's|try_files $uri $uri/ =404;|proxy_pass http://localhost:5000;|g' \
/etc/nginx/sites-available/default
sudo systemctl restart nginx
```

### 8. Start App with pm2
```bash
pm2 start "gunicorn --bind 0.0.0.0:5000 weather_api:app" --name weather-api
```

### 9. Test
Visit in browser:
```
http://YOUR_PUBLIC_IP/weather?postcode=SW1A1AA
```

---

## Example Response

```json
{
  "postcode": "SW1A1AA",
  "vibe": "its giving summer bestie",
  "advice": "cute outfit weather, light layers at most",
  "condition": "clear sky",
  "temp_c": 25.84,
  "feels_like_c": 25.5,
  "humidity_percent": 39,
  "wind_mps": 2.24
}
```

---

## What I Learned

- The deployment pattern is reusable across languages
- Only the runtime, package manager, and start command change
- gunicorn is the Python equivalent of running a Node app in production
- The API key must never be in version control — transfer separately
- pm2 works for any process, not just Node

---

## Stack

- Ubuntu 26.04 on AWS EC2
- Python 3 + Flask
- gunicorn (WSGI server)
- nginx (reverse proxy)
- pm2 (process manager)
- Postcodes.io API
- OpenWeatherMap API
```

