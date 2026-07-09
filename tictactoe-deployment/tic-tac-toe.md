# Tic Tac Toe Deployment

## VM Set Up
sudo apt update -y
sudo apt upgrade -y

# Install nginx
sudo apt install nginx -y

# Install Node JS v20
curl -sL https://deb.nodesource.com/setup_20.x -o nodesource_setup.sh
sudo bash nodesource_setup.sh
sudo apt install nodejs -y

sudo apt install unzip -y
unzip nodejs20-sparta-tictactoe-v1-2.zip

## Run the App
cd app
npm install
npm start

## Notes
- Running npm install triggered a postinstall hook (seeds/seed.js)
  that automatically seeded the scoreboard with default placeholder
  data (e.g. AAA/100, BBB/200) before the app was even started.
