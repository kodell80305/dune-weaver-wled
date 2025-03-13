import os
import shutil
import sys
import pwd
import grp
import filecmp

# Define the path for the systemd service file
service_file_path = '/etc/systemd/system/dune-weaver-wled.service'
# Use the current working directory
working_directory = os.getcwd()
local_service_file = 'dune-weaver-wled.service'

# Get the current working directory
current_working_directory = os.getcwd()

# Content of the systemd service file
service_file_content = f"""
[Unit]
Description=Dune Weaver WLED Application
After=network.target

[Service]
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/usr/bin/python3 {current_working_directory}/app.py
WorkingDirectory={current_working_directory}
Restart=always
RestartSec=10
StartLimitInterval=0
User=root
Group=root

[Install]
WantedBy=multi-user.target
"""

def set_permissions():
    uid = pwd.getpwnam("root").pw_uid
    gid = grp.getgrnam("root").gr_gid
    os.chown(working_directory, uid, gid)
    for root, dirs, files in os.walk(working_directory):
        for dir_ in dirs:
            os.chown(os.path.join(root, dir_), uid, gid)
        for file_ in files:
            # Skip files created by build_web.py
            if 'build_web.py' not in file_:
                os.chown(os.path.join(root, file_), uid, gid)

def check_index_file():
    index_file_path = os.path.join(working_directory, 'templates/index.htm')
    if not os.path.exists(index_file_path):
        print(f"Error: {index_file_path} not found. Running build_web.py...")
        build_web_script = os.path.join(working_directory, 'build_web.py')
        # Get the owner of the working directory
        dir_owner = pwd.getpwuid(os.stat(working_directory).st_uid).pw_name
        # Run build_web.py as the directory owner
        if os.system(f'su -c "python3 {build_web_script}" {dir_owner}') != 0:
            print("Error: Failed to run build_web.py.")
            sys.exit(1)
        if not os.path.exists(index_file_path):
            print(f"Error: {index_file_path} still not found after running build_web.py.")
            sys.exit(1)

def install_requirements():
    requirements_file = os.path.join(working_directory, 'requirements.txt')
    if os.path.exists(requirements_file):
        print("Installing packages from requirements.txt...")
        if os.system(f'python3 -m pip install --break-system-packages -r {requirements_file}') != 0:
            print("Error: Failed to install required packages.")
            sys.exit(1)
    else:
        print("requirements.txt not found. Skipping package installation.")

def create_service():
    # Write the systemd service file locally
    with open(local_service_file, 'w') as service_file:
        service_file.write(service_file_content)

    # Check if the service file exists and if it has changed
    if not os.path.exists(service_file_path) or not filecmp.cmp(local_service_file, service_file_path):
        # Copy the service file to the systemd directory
        shutil.copy(local_service_file, service_file_path)
        print("Systemd service file created/updated successfully.")

    # Set the correct permissions for the working directory
    #set_permissions()

    # Reload systemd, enable and start the service
    os.system('systemctl daemon-reload')
    os.system('systemctl enable dune-weaver-wled.service')
    print("Systemd service for Dune Weaver WLED Application has been set up successfully.")

def start_service():
    install_requirements()
    check_index_file()
    create_service()
    os.system('systemctl start dune-weaver-wled.service')
    print("Systemd service for Dune Weaver WLED Application started.")

def stop_service():
    os.system('systemctl stop dune-weaver-wled.service')
    print("Systemd service for Dune Weaver WLED Application stopped.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python startService.py <start|stop>")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == "start":
        start_service()
    elif action == "stop":
        stop_service()
    else:
        print("Invalid argument. Use 'start' or 'stop'.")
        sys.exit(1)
