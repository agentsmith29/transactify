#!/bin/bash
echo "Im User $(whoami) and I am shutting down the system."
echo "o" > /proc/sysrq-trigger