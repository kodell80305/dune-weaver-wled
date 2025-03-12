#!/bin/bash

# Define the file to be patched
file_path="~/dune-weaver/modules/connection/connection_manager.py"

# Define the code to be inserted
insert_code=$(cat << 'EOF'
def get_comports(include_links=False):
    import glob
    from serial.tools.list_ports_linux import SysFS

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

# Insert the code before the function list_serial_ports()
sed -i "/def list_serial_ports()/i $insert_code" "$file_path"

# Comment out the line ports = serial.tools.list_ports.comports() and add ports = comports immediately after
sed -i "/ports = serial.tools.list_ports.comports()/s/^/#/" "$file_path"
sed -i "/#ports = serial.tools.list_ports.comports()/a ports = get_comports()" "$file_path"

echo "Patch applied successfully."