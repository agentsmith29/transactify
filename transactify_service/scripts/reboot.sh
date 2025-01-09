#!/bin/bash
echo "Im User $(whoami) and I am rebootin down the system."
echo "b" > /proc/sysrq-trigger