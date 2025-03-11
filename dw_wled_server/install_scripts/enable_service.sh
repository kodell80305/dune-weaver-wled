#!/bin/bash

SERVICE_FILE="/etc/systemd/system/dune-weaver.service"

# Create the service file
cat <<EOL > $SERVICE_FILE
[Unit]
Description=Dune Weaver Backend
After=network.target

[Service]
ExecStart=/home/pi/dune-weaver/.venv/bin/python /home/pi/dune-weaver/app.py
WorkingDirectory=/home/pi/dune-weaver
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd manager configuration
systemctl daemon-reload
systemctl enable dune-weaver
systemctl start dune-weaver
systemctl status dune-weaver

echo "Service file created and systemd reloaded."