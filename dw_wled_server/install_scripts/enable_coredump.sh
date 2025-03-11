#!/bin/bash

# Define the configuration file path
CONFIG_FILE="/etc/sysctl.d/core.conf"
LIMITS_FILE="/etc/security/limits.conf"

# Create or edit the configuration file with the required settings
cat <<EOL > $CONFIG_FILE
kernel.core_pattern = /var/lib/coredumps/core-%e-sig%s-user%u-group%g-pid%p-time%t
kernel.core_uses_pid = 1
fs.suid_dumpable = 2
EOL

# Create the directory for core dumps and set permissions
mkdir -p /var/lib/coredumps/
chmod 777 /var/lib/coredumps/

# Apply the new sysctl settings
sysctl --system

# Add the line to /etc/security/limits.conf if it doesn't already exist
if ! grep -q "^*  soft  core  unlimited" $LIMITS_FILE; then
    echo "*  soft  core  unlimited" >> $LIMITS_FILE
fi

echo "Core dump settings have been updated and applied."