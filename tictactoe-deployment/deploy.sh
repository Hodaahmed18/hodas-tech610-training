#!/bin/bash

echo " Starting deployment..."

echo " Updating system packages..."
sudo apt update -y &>/dev/null && sudo apt upgrade -y &>/dev/null

echo " Installing nginx..."
sudo apt install nginx -y &>/dev/null

echo " Installing unzip..."
sudo apt install unzip -y &>/dev/null

echo " Downloading Node.js setup script..."
curl -sL https://deb.nodesource.com/setup_20.x -o nodesource_setup.sh &>/dev/null

echo " Configuring Node.js repository..."
sudo bash nodesource_setup.sh &>/dev/null

echo " Installing Node.js v20..."
sudo apt install nodejs -y &>/dev/null

echo " Unzipping app..."
unzip nodejs20-sparta-tictactoe-v1-2.zip &>/dev/null

echo " Installing app dependencies..."
cd app
npm install &>/dev/null

echo " Configuring the nginx reverse proxy..."
sudo sed -i 's|try_files $uri $uri/ =404;|proxy_pass http://localhost:3000;|g' /etc/nginx/sites-available/default
sudo systemctl restart nginx &>/dev/null

echo "Starting app with pm2..."
sudo npm install -g pm2 &>/dev/null
pm2 start index.js

echo " All done. App running on port 80."
