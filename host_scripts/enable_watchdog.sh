#!/bin/bash

# Define the file path
CONFIG_FILE="/boot/firmware/config.txt"
PARAM="dtparam=watchdog"
VALUE="on"

# Function to check if the parameter exists and set it
enable_watchdog() {
    echo "Configuring $PARAM=$VALUE in $CONFIG_FILE..."

    # Check if the parameter exists in the file
    if grep -q "^$PARAM=" "$CONFIG_FILE"; then
        echo "Parameter $PARAM exists. Updating its value to $VALUE."
        # Update the parameter value
        sudo sed -i "s/^$PARAM=.*/$PARAM=$VALUE/" "$CONFIG_FILE"
    else
        echo "Parameter $PARAM does not exist. Adding it to the file."
        # Append the parameter to the file
        echo "$PARAM=$VALUE" | sudo tee -a "$CONFIG_FILE" > /dev/null
    fi

    # Verify the change
    if grep -q "^$PARAM=$VALUE" "$CONFIG_FILE"; then
        echo "Parameter $PARAM has been successfully set to $VALUE."
    else
        echo "Failed to set $PARAM=$VALUE. Please check $CONFIG_FILE manually."
        exit 1
    fi
}

# Execute the function
enable_watchdog
