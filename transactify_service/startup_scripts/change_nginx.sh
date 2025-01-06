#!/bin/bash

FILE_NGINX_CONF="$1"

# check if a file is given and if it exists
if [ -z "$FILE_NGINX_CONF" ]; then
    echo "Error: Variable FILE_NGINX_CONF must be set."
    exit 1
fi

if [ ! -f "$FILE_NGINX_CONF" ]; then
    echo "Error: $FILE_NGINX_CONF does not exist."
    exit 1
fi



# Check if required environment variables are set
if [[ -z "$SERVICE_NAME" || -z "$DJANGO_WEB_PORT" ]]; then
    echo "Error: SERVICE_NAME and DJANGO_WEB_PORT must be set."
    exit 1
fi


# Backup the original file
cp "$FILE_NGINX_CONF" "${FILE_NGINX_CONF}.bak"

# Replace placeholders in the file
echo "Replacing location with $SERVICE_NAME in $FILE_NGINX_CONF..."
sed -i "s|<location>|$SERVICE_NAME|g" "$FILE_NGINX_CONF"

echo "Replacing host with $HOSTNAME in $FILE_NGINX_CONF..."
sed -i "s|<host>|$HOSTNAME|g" "$FILE_NGINX_CONF"

echo "Replacing port with $DJANGO_WEB_PORT in $FILE_NGINX_CONF..."
sed -i "s|<port>|$DJANGO_WEB_PORT|g" "$FILE_NGINX_CONF"

echo "Placeholders replaced successfully in $FILE_NGINX_CONF."

cat $FILE_NGINX_CONF
