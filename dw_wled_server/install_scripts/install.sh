#!/bin/bash

# Update package lists
sudo apt update && sudo apt upgrade -y

# Install necessary packages
sudo apt-get install -y git curl python3-venv

# Install Docker, just so we have it, but don't enable it for now
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Clone the repository
git clone -b dlc32 -https://github.com/tuanchris/dune-weaver.git ~dune-weaver

# Navigate to the project directory
cd ~dune-weaver

# Create and activate a virtual environment
python3 -m venv ./venv
source ./venv/bin/activate

# Install additional dependencies
pip install pystack pytest-pystack

# Install project dependencies
pip install -r requirements.txt

echo "Installation completed successfully."