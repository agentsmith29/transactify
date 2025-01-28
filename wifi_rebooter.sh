#!/bin/bash

# Name of the hotspot connection
HOTSPOT_NAME="hotspot"

# Function to enable the hotspot
enable_hotspot() {
    echo "No Wi-Fi connection detected. Enabling hotspot..."
    sudo nmcli con up "$HOTSPOT_NAME"
}

# Function to check Wi-Fi connection
check_wifi() {
    # Get the Wi-Fi connection status
    WIFI_STATUS=$(nmcli -t -f ACTIVE,TYPE con | grep '^yes:wifi' | cut -d: -f2)
    
    if [[ "$WIFI_STATUS" == "wifi" ]]; then
        echo "Wi-Fi is connected."
        return 0
    else
        echo "Wi-Fi is not connected."
        return 1
    fi
}

# Main logic
if check_wifi; then
    echo "No need to enable hotspot."
else
    enable_hotspot
fi
