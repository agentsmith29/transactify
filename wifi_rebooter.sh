#!/bin/bash

# The IP for the server you wish to ping. I suggest an internal gateway.
# get the gateway from eth0 and wlan0
SERVER=$(ip route show | grep default | awk '{print $3}')

# Only send two pings, sending output to /dev/null
ping -c2 ${SERVER} > /dev/null

# If the return code from ping ($?) is not 0 (meaning there was an error)

if [ $? != 0 ]
then
    current_date=$(date)
    # Restart the wireless interface
    echo "(!) [${current_date}] Ping to server ${SERVER} failed." >> /home/pi/ping.log
    ip link set wlan0 down >> /home/pi/ping.log
    sleep 1
    ip link set wlan0 up >> /home/pi/ping.log
    echo "(!) [${current_date}] Restarted wifi" >> /home/pi/ping.log
else
    current_date=$(date)
    echo "(+) [${current_date}] Ping server ${SERVER} successful" >> /home/pi/ping.log
fi