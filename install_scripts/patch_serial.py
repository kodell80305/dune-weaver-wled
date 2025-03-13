import os
import tempfile

#git describe --tags --abbrev=0 origin/main  myversion'
#git checkout --force v2.03       force specific tag
#git fetch tags --force
#don't trust this code ... need to retest

#code to insert after available_ports line 
#    if(not available_ports):
#        import glob
#        available_ports = glob.glob('/dev/ttyS*') 
#        logger.info(f"available_ports={available_ports}")


file_path = os.path.expanduser('~/dune-weaver/modules/connection/connection_manager.py')
docker_compose_path = os.path.expanduser('~/dune-weaver/docker-compose.yml')


portStr = "ports = serial.tools.list_ports.comports()"
newPort =    "ports = glob.glob('dev/ttyS')    #serial.tools.list_ports.comports()\n"

# Check if the file has already been modified
with open(file_path, 'r') as file:
    # Check if the file has already been modified
    lines = file.readlines()

if (newPort in lines):
    print("The file has already been modified. Skipping patch.")

else:
    with open(file_path, 'w') as file:
        for line in lines:
            if (portStr in line):
                print(portStr)
                line =line.replace(portStr, newPort)
                print("Serial patch applied successfully.  ", line, newPort)
            
            file.write(line)

# Patch the docker-compose.yml file to add a line after devices:
    
devString =  "    - \"/dev/ttyS0:/dev/ttyS0\"\n"


with open(docker_compose_path, 'r') as file:
    lines = file.readlines()

with open(docker_compose_path, 'w') as file:

        if (devString in lines):
            print("The file has already been modified. Skipping patch.")
            exit(0)

        for line in lines:
            file.write(line)

            if("devices:") in line:
                file.write(devString)
                print("docker-compose.yml patched successfully.")


