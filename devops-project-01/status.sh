#!/bin/bash

# System Status Page Generator 
# Outputs HTML with live server metrics
# Author: Hoda Xirsi

echo "<!DOCTYPE html>"
echo "<html>"
echo "<head><title>Server Status</title></head>"
echo "<body>"
echo "<style>"
echo "body { font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff88; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }"
echo ".container { max-width: 600px; padding: 40px; }"
echo "h1 { font-size: 28px; margin-bottom: 24px; }"
echo ".stat { background: #111; border-left: 3px solid #00ff88; padding: 12px 16px; margin-bottom: 12px; }"
echo ".label { color: #666; font-size: 11px; letter-spacing: 2px; }"
echo ".value { font-size: 16px; margin-top: 4px; }"
echo "</style>"
echo "<div class='container'>"
echo "<h1>System Status</h1>"

echo "<div class='stat'><div class='label'>UPTIME</div><div class='value'>$(uptime -p)</div></div>"
echo "<div class='stat'><div class='label'>DISK USAGE</div><div class='value'>$(df -h / | awk 'NR==2 {print $3 " used of " $2 " (" $5 ")"}')</div></div>"
echo "<div class='stat'><div class='label'>MEMORY</div><div class='value'>$(free -h | awk '/Mem:/ {print $3 " used of " $2}')</div></div>"
echo "<div class='stat'><div class='label'>TOP PROCESS</div><div class='value'>$(ps aux --sort=-%cpu | awk 'NR==2 {print $11}')</div></div>"

echo "</div>"
echo "</body>"
echo "</html>"
