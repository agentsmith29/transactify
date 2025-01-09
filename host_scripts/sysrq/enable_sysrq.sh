#!/bin/bash

# Define the sysctl configuration directory and file
SYSCTL_DIR="/etc/sysctl.d"
SYSCTL_CONF="${SYSCTL_DIR}/99-sysrq.conf"
SYSRQ_PARAM="kernel.sysrq"
SYSRQ_VALUE="1"

# Create the sysctl.d directory if it doesn't exist
if [ ! -d "$SYSCTL_DIR" ]; then
    echo "Creating sysctl.d directory at $SYSCTL_DIR..."
    sudo mkdir -p "$SYSCTL_DIR"
fi

# Enable sysrq immediately by writing to /proc/sys/kernel/sysrq
echo "Enabling /proc/sysrq-trigger..."
if echo "$SYSRQ_VALUE" | sudo tee /proc/sys/kernel/sysrq > /dev/null; then
    echo "/proc/sysrq-trigger is now enabled."
else
    echo "Failed to enable /proc/sysrq-trigger. Please check permissions."
    exit 1
fi

# Persist the setting in /etc/sysctl.d/99-sysrq.conf
echo "Persisting $SYSRQ_PARAM = $SYSRQ_VALUE in $SYSCTL_CONF..."
echo "$SYSRQ_PARAM = $SYSRQ_VALUE" | sudo tee "$SYSCTL_CONF" > /dev/null

# Apply sysctl settings
echo "Applying sysctl settings..."
if sudo sysctl --system > /dev/null; then
    echo "Sysctl settings applied successfully."
else
    echo "Failed to apply sysctl settings. Please check $SYSCTL_CONF."
    exit 1
fi

echo "/proc/sysrq-trigger has been successfully enabled and persisted."
