# 🖥️ Live Server Status Dashboard

A Dockerised nginx web server that serves a live system monitoring dashboard via a bash CGI script.

Visit the running container in a browser and see real-time server metrics — uptime, disk usage, memory, and top process — rendered as a styled HTML page generated entirely by bash.

---

## 🚀 What It Does

- Runs nginx inside a Docker container
- Serves a bash script as a CGI endpoint via FastCGI
- The bash script generates a live HTML status page on every request
- Displays real server metrics pulled at request time

---

## 🖥️ What You See

| Metric | Source Command |
|--------|---------------|
| Uptime | `uptime -p` |
| Disk Usage | `df -h /` |
| Memory | `free -h` |
| Top Process | `ps aux --sort=-%cpu` |

---

## 📂 Files

| File | Description |
|------|-------------|
| `Dockerfile` | Builds the image — installs bash, fcgiwrap, copies scripts, sets up CGI |
| `nginx.conf` | Configures nginx to pass all requests to the bash script via FastCGI |
| `status.sh` | Bash script that generates the HTML status page with live metrics |

---

## ⚙️ How It Works

```
Browser request
      ↓
nginx (port 80)
      ↓
FastCGI (fcgiwrap on port 9000)
      ↓
status.sh (bash script runs, outputs HTML)
      ↓
Browser receives live HTML page
```

nginx doesn't serve a static file — it passes every request to `fcgiwrap`, which executes `status.sh` and returns whatever it prints. The script uses bash commands to pull live system metrics and wraps them in HTML.

---

## 🐳 Run It

```bash
# Build the image
docker build -t server-status .

# Run the container
docker run -p 80:80 server-status
```

Then visit `http://localhost` in your browser.

---

## 🛠️ Tech Stack

- Docker
- nginx (alpine)
- Bash
- FastCGI (fcgiwrap + spawn-fcgi)
- CGI scripting

---

