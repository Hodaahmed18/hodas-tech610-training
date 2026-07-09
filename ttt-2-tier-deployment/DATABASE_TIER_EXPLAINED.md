# Provisioning MongoDB on Ubuntu 24.04 VM

Always use `#!/bin/bash` at the top of your bash script (especially when using it for user data on AWS) so Linux knows it needs to use the bash interpreter.

## Step 1
These commands will update the list of available packages (update) and update your installed packages to the newest versions (upgrade).
```
sudo apt-get update -y
sudo apt-get upgrade -y
```

## Step 2
This command will import the MongoDB public GPG key.
```
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
   --dearmor
```
A GPG key is used in Linux to verify the authenticity and integrity of software. This means it will ensure the application we are downloading was officially published by the developers and has not been corrupted by malicious third parties.

Note: use `pgp.mongodb.com`, not `pgp.mongodb.org`. The `.org` address no longer serves the key, it silently returns MongoDB's homepage instead, which breaks this step with no obvious error.

## Step 3
This command will create a list file, adding MongoDB to your list of available packages.
```
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.2.list
```
The version number in this repo line (`8.2`) must match the version pinned on the packages in Step 5 (`8.2.5`). If they don't match, apt won't be able to locate the packages.

## Step 4
We need to run this update command to update our list of packages so MongoDB can be installed.
```
sudo apt-get update
```

## Step 5
This command will install MongoDB 8.2.5
```
echo Installing MongoDB...
sudo apt-get install -y \
   mongodb-org=8.2.5 \
   mongodb-org-database=8.2.5 \
   mongodb-org-server=8.2.5 \
   mongodb-mongosh \
   mongodb-org-shell=8.2.5 \
   mongodb-org-mongos=8.2.5 \
   mongodb-org-tools=8.2.5 \
   mongodb-org-database-tools-extra=8.2.5
echo Installed MongoDB!
```

## Step 6
The below command will show the status of MongoDB, we will primarily be using this to check if the database is running.
```
sudo systemctl status mongod
```
This next command will start the database.
```
sudo systemctl start mongod
```
This command will make MongoDB start automatically during system boot.
```
sudo systemctl enable mongod
```
