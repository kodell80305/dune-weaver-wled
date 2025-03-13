import os
import tempfile

file_path = os.path.expanduser('~/dune-weaver/modules/connection/connection_manager.py')
docker_compose_path = os.path.expanduser('~/dune-weaver/docker-compose.yml')

# Check if the file has already been modified
with open(file_path, 'r') as file:
    if "def get_comports(include_links=False):" in file.read():
        print("The file has already been modified. Skipping patch.")
        exit(0)

# Define the code to be inserted
insert_code = """
def get_comports(include_links=False):
    import glob
    from serial.tools.list_ports_linux import SysFS
    from serial.tools import list_ports_common, list_links

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
            for info in [SysFS(d) for d in devices]]
    """


# Create a temporary file to store the insert code
with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    temp_file.write(insert_code.encode())
    temp_file_path = temp_file.name

# Insert the code before the function list_serial_ports()
with open(file_path, 'r') as file:
    lines = file.readlines()

with open(file_path, 'w') as file:
    for line in lines:
        if "def list_serial_ports()" in line:
            file.write(insert_code)
        file.write(line)

# Comment out the line ports = serial.tools.list_ports.comports() and add ports = get_comports immediately after
with open(file_path, 'r') as file:
    lines = file.readlines()

with open(file_path, 'w') as file:
    for line in lines:
        if "ports = serial.tools.list_ports.comports()" in line:
            file.write("#" + line)
            file.write("    ports = get_comports()\n")
        else:
            file.write(line)

print("Serial patch applied successfully.")

# Patch the docker-compose.yml file to add a line after devices:
# also need to comment out image line
with open(docker_compose_path, 'r') as file:
    lines = file.readlines()

with open(docker_compose_path, 'w') as file:
    for line in lines:
        file.write(line)
        if "devices:" in line:
            file.write("  - /dev/ttyS0:/dev/ttyS0\n")

print("docker-compose.yml patched successfully.")

# Patch the docker-compose.yml file to add a line after /dev/ttyACM0
with open(docker_compose_path, 'r') as file:
    content = file.read()

content = content.replace("- /dev/ttyACM0", "- /dev/ttyACM0\n      - \"/dev/ttyS0:/dev/ttyS0\"")

with open(docker_compose_path, 'w') as file:
    file.write(content)

print("docker-compose.yml patched successfully.")
