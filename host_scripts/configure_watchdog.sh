#!/bin/bash
WATCHDOG_CONF="/etc/watchdog.conf"

set_watchdog_conf() {
    PARAM="$1"
    VALUE="$2"

    if [ -z "$PARAM" ] || [ -z "$VALUE" ]; then
        echo "Error: Missing parameter or value. Usage: set_watchdog_conf <param> <value>"
        return 1
    fi

    # Construct the full parameter line
    CONFIG_LINE="${PARAM} = ${VALUE}"

    echo "Configuring ${CONFIG_LINE} in ${WATCHDOG_CONF}..."

    # Check if the exact parameter exists as an uncommented line
    if grep -qE "^\s*${PARAM}\s*=" "$WATCHDOG_CONF"; then
        echo "Parameter ${PARAM} exists. Updating its value."
        sudo sed -i "s|^\s*${PARAM}\s*=.*|${CONFIG_LINE}|" "$WATCHDOG_CONF"

    # Check if the exact parameter exists as a commented line
    elif grep -qE "^\s*#\s*${PARAM}\s*=" "$WATCHDOG_CONF"; then
        echo "Parameter ${PARAM} is commented. Uncommenting and updating."
        sudo sed -i "s|^\s*#\s*${PARAM}\s*=.*|${CONFIG_LINE}|" "$WATCHDOG_CONF"

    else
        echo "Adding new parameter: ${CONFIG_LINE}"
        echo "$CONFIG_LINE" | sudo tee -a "$WATCHDOG_CONF" > /dev/null
    fi

    # Verify the change
    if grep -qE "^\s*${CONFIG_LINE}" "$WATCHDOG_CONF"; then
        echo "Successfully configured ${CONFIG_LINE} in ${WATCHDOG_CONF}."
    else
        echo "Failed to configure ${CONFIG_LINE} in ${WATCHDOG_CONF}."
        return 1
    fi
}

enable_watchdog_service_on_boot() {
    WATCHDOG_SERVICE="/lib/systemd/system/watchdog.service"

    echo "Configuring $WATCHDOG_SERVICE for boot..."

    # Ensure the [Install] section exists and add the required lines
    if ! grep -q "^\[Install\]" "$WATCHDOG_SERVICE"; then
        echo "Adding [Install] section to $WATCHDOG_SERVICE"
        echo -e "\n[Install]\nWantedBy=multi-user.target" | sudo tee -a "$WATCHDOG_SERVICE" > /dev/null
    elif ! grep -q "^WantedBy=multi-user.target" "$WATCHDOG_SERVICE"; then
        echo "Updating [Install] section in $WATCHDOG_SERVICE"
        sudo sed -i '/^\[Install\]/a WantedBy=multi-user.target' "$WATCHDOG_SERVICE"
    fi

    # Reload systemd to pick up changes and enable watchdog service
    echo "Reloading systemd and enabling watchdog service..."
    sudo systemctl daemon-reload
    sudo systemctl enable watchdog

    echo "Watchdog service configured to start on boot."
}

set_watchdog_conf "max-load-1" "24"
set_watchdog_conf "min-memory" "1"
set_watchdog_conf "watchdog-device" "/dev/watchdog"
set_watchdog_conf "watchdog-timeout" "15"
# Add watchdog on boot (apparently it already runs...)
# enable_watchdog_service_on_boot
