#!/bin/bash

# Define the file to be patched
file_path=~/dune-weaver/modules/connection/connection_manager.py
docker_compose_path=~/dune-weaver/docker-compose.yml

# Check if the file has already been modified
if grep -q "def get_comports(include_links=False):" "$file_path"; then
    echo "The file has already been modified. Skipping patch."
    exit 0
fi


# Define the code to be inserted
insert_code=$(cat << 'EOF'
def get_comports(include_links=False):
    import glob
    from serial.tools.list_ports_linux import SysFS
    from serial.tools.list_ports_common import list_ports_common, list_links

    devices = glob.glob('/dev/ttyS*')           # built-in serial ports
    devices.extend(glob.glob('/dev/ttyUSB*'))   # usb-serial with own driver
    devices.extend(glob.glob('/dev/ttyXRUSB*')) # xr-usb-serial port exar (DELL Edge 3001)
    devices.extend(glob.glob('/dev/ttyACM*'))   # usb-serial with CDC-ACM profile
    devices.extend(glob.glob('/dev/ttyAMA*'))   # ARM internal port (raspi)
    devices.extend(glob.glob('/dev/rfcomm*'))   # BT serial devices
    devices.extend(glob.glob('/dev/ttyAP*'))    # Advantech multi-port serial controllers
    if include_links:
        devices.extend(list_ports_common.list_links(devices))
    return [info
EOF
)

# Create a temporary file to store the insert code
temp_file=$(mktemp)
echo "$insert_code" > "$temp_file"

# Insert the code before the function list_serial_ports()
sed -i "/def list_serial_ports()/r $temp_file" "$file_path"


# Comment out the line ports = serial.tools.list_ports.comports() and add ports = comports immediately after
sed -i "/ports = serial.tools.list_ports.comports()/s/^/#/" "$file_path"
sed -i "/#ports = serial.tools.list_ports.comports()/a ports = get_comports()" "$file_path"

echo "Serial patch applied successfully."

# Patch the docker-compose.yml file to add a line after devices:
#also need to comment out image line
if grep -q "devices:" "$docker_compose_path"; then
    sed -i "/devices:/a \ \ - /dev/ttyS0:/dev/ttyS0" "$docker_compose_path"
    echo "docker-compose.yml patched successfully."
else
    echo "devices: line not found in docker-compose.yml. Skipping patch."
fi

echo "Serial patch applied successfully."

# Patch the docker-compose.yml file to add a line after /dev/ttyACM0
perl -i -pe 's|(\s*- /dev/ttyACM0)|$1\n      - "/dev/ttyS0:/dev/ttyS0"|' "$docker_compose_path"

echo "docker-compose.yml patched successfully."