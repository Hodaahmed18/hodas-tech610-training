# 🎮 Tic Tac Toe - Cloud Deployment
Node.js App Deployment on AWS UBUNTU EC2

End-to-end automated deployment of a Node.js application onto a fresh Ubuntu EC2 instance, including nginx reverse proxy configuration and process management with pm2.

## 🚀 Project Overview
This project demonstrates a full manual-to-automated deployment pipeline where I:
- Provisioned and secured a fresh Ubuntu EC2 instance on AWS
- Wrote a bash script to fully automate the environment setup
- Configured nginx as a reverse proxy (port 80 → port 3000)
- Used pm2 to run the app headlessly so it survives terminal disconnects
- Documented the full deployment process

## 🖥️ Environment
| Component | Detail |
|-----------|--------|
| OS | Ubuntu 26.04 |
| Cloud | AWS EC2 (t3.micro) |
| Region | eu-west-1 |
| Access | SSH (key-based authentication) |

## 📂 Repository Structure
| File | Description |
|------|-------------|
| `deploy.sh` | Fully automated deployment script |
| `tic-tac-toe.md` | Step-by-step deployment documentation |
| `README.md` | Project overview |

## 🔧 What the Script Does
- Updates and upgrades system packages
- Installs nginx, Node.js v20, and unzip
- Downloads and runs the NodeSource setup script to pin Node v20
- Unzips the application
- Installs app dependencies via npm
- Configures nginx as a reverse proxy using `sed` to edit the config file automatically
- Restarts nginx to apply changes
- Installs pm2 globally and starts the app as a background process

## ▶️ How to Use
1. Spin up a fresh Ubuntu EC2 instance
2. Open ports 22 (SSH), 80 (HTTP) and 3000 in your security group
3. SCP the app zip file onto the instance
4. SCP this script onto the instance
5. Run:
```bash
chmod +x deploy.sh && ./deploy.sh
```
6. Visit your public IP in a browser - no port number needed

## 🛠️ Tech Stack
- Ubuntu 26.04 on AWS EC2
- Node.js v20 (via NodeSource)
- nginx (reverse proxy)
- pm2 (process manager)
- Bash scripting
- Git & GitHub

## 🔐 Security
- SSH locked to specific IP on port 22
- Security group configured with least privilege
- nginx handles public traffic, app runs internally on port 3000

## 📌 What I Learned
- How to manually deploy a Node.js app to a cloud server end to end
- How nginx works as a reverse proxy
- How to automate deployment steps using bash and sed
- How pm2 keeps apps running headlessly in production
