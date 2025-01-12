#!/bin/bash

AUTOCONF_DIR="/etc/nginx/autoconf"
CONFD_DIR="/etc/nginx/conf.d"

echo "Contents of ${AUTOCONF_DIR}"
ls -l ${AUTOCONF_DIR}
# Copy all autoconf files to conf.d
# check if autoconf directory is empty
if [ "$(ls -A $AUTOCONF_DIR)" ]; then
    echo "Directory $AUTOCONF_DIR is not empty"
    # Remove all old autoconf files
    echo "Removing all old autoconf files in ${CONFD_DIR}"
    # use regex to remove all files starting with nginx. and ending with .conf
    # use the find command
    find ${CONFD_DIR} -type f -name "nginx.*.conf" -exec rm -f {} \;
    echo "Contents of ${CONFD_DIR}"
    ls -l ${CONFD_DIR}
    cp -r ${AUTOCONF_DIR}/* ${CONFD_DIR}/

    # Then remove all autoconf files
    find ${AUTOCONF_DIR} -type f -name "*.conf" -exec rm -f {} \;
else
    echo "Directory $AUTOCONF_DIR is empty, exiting..."
fi


echo "Contents of ${AUTOCONF_DIR}"
ls -l ${AUTOCONF_DIR}
echo "Contents of ${CONFD_DIR}"
ls -l ${CONFD_DIR}