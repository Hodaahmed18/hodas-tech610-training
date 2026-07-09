#!/bin/bash
export MONGODB_URI=mongodb://172.31.59.103:27017/tictactoe
export STATEFUL_MODE=server
pm2 start /home/ubuntu/app/app/index.js
