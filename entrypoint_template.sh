#!/bin/bash
set -e
# Ensure the necessary environment variables are set
# export DJANGO_SETTINGS_MODULE=terminal.settings
export HOSTNAME=$(hostname)
DOCKERINFO=$(curl -s --unix-socket /run/docker.sock http://docker/containers/$HOSTNAME/json)
# echo "DOCKERINFO: $DOCKERINFO"
export CONTAINER_NAME=$(echo "$DOCKERINFO" | jq -r '.Name' | sed 's|/||')

echo "Starting container $CONTAINER_NAME (id $HOSTNAME).."


PYTHON_EXEC=python
MANAGE_PY="$PYTHON_EXEC manage.py"

# Directories
export DIR_COMMON="/common"
export DIR_STATIC="/app/static"
export DIR_SCRIPTS="${DIR_COMMON}/scripts"
export DIR_NGINX="${DIR_COMMON}/nginx"
export DIR_SHARED_CONFIG="/etc/nginx/conf.d"

# Files 
export FILE_NGINX_CONF="$DIR_NGINX/templates/nginx.template.conf"
export FILE_NGINX_CONF_STORE="$DIR_SHARED_CONFIG/nginx.${CONTAINER_NAME}.conf"

# Scripts
export SH_CHANGE_NGINX="$DIR_SCRIPTS/change_nginx.sh"
export PY_CHANGE_NGINX="$DIR_SCRIPTS/change_nginx.py"
export SH_MAKE_STORE_MIGRATION="$DIR_SCRIPTS/db_migration.sh"
export SH_RESET_DATABSE_SCRIPT="$DIR_SCRIPTS/reset_database.sh"


mkdir -p $DIR_SHARED_CONFIG
# =====================================================================================================================
# =====================================================================================================================
# Check if all files and directories exist
if [ ! -d "$DIR_STATIC" ]; then
    echo "Error: $DIR_STATIC does not exist."
    exit 1
fi

if [ ! -d "$DIR_SCRIPTS" ]; then
    echo "Error: $DIR_SCRIPTS does not exist."
    exit 1
fi

if [ ! -d "$DIR_NGINX" ]; then
    echo "Error: $DIR_NGINX does not exist."
    exit 1
fi

if [ ! -d "$DIR_SHARED_CONFIG" ]; then
    echo "Error: $DIR_SHARED_CONFIG does not exist."
    exit 1
fi

if [ ! -f "$FILE_NGINX_CONF" ]; then
    echo "Error: $FILE_NGINX_CONF does not exist."
    exit 1
fi

if [ ! -f "$SH_CHANGE_NGINX" ]; then
    echo "Error: $SH_CHANGE_NGINX does not exist."
    exit 1
fi

if [ ! -f "$SH_MAKE_STORE_MIGRATION" ]; then
    echo "Error: $SH_MAKE_STORE_MIGRATION does not exist."
    exit 1
fi



# =====================================================================================================================
# Regmigration of the database, if REMIGRATE is set to true
# =====================================================================================================================
# check if REMIGRATE is set or available

if [ -z "$DB_RESET" ]; then
    echo "DB_RESET is not set. Setting DB_RESET to false..."
    DB_RESET="false"
fi

# if statement to check if REMIGRATE is set to true
chmod +x $SH_RESET_DATABSE_SCRIPT
if [ "$DB_RESET" = "true" ]; then
    echo "Resetting the database using $SH_RESET_DATABSE_SCRIPT... also remigrating the database..."
    $SH_RESET_DATABSE_SCRIPT
    REMIGRATE="true"
fi



if [ -z "$REMIGRATE" ]; then
    echo "REMIGRATE is not set. Setting REMIGRATE to false..."
    REMIGRATE="false"
fi

# if statement to check if REMIGRATE is set to true
chmod +x $SH_MAKE_STORE_MIGRATION
if [ "$REMIGRATE" = "true" ]; then
    echo "Remigrating the database using $SH_MAKE_STORE_MIGRATION..."
    $SH_MAKE_STORE_MIGRATION
fi



# ========================================
# Collect static files
# ========================================
echo "Collecting static files..."
rm -rf  $DIR_STATIC/* || {
    echo "ERROR: Failed remove files in $DIR_STATIC"
}

echo "Copying staticfiles to  $DIR_STATIC..."
cp -r /app/staticfiles/* $DIR_STATIC/ || {
    echo "ERROR: Failed copy staticfiles to $DIR_STATIC"
    exit 1
}

$MANAGE_PY collectstatic --noinput || {
    echo "ERROR: Failed to collect static files."
    exit 1
}


# Alter the nginx configuration file to use the correct port
echo "Changing the port in the nginx configuration file using the script $SH_CHANGE_NGINX..."
chmod +x $SH_CHANGE_NGINX || {
    echo "ERROR: Failed to change the port in the nginx configuration file."
    exit 1
}

python $PY_CHANGE_NGINX $FILE_NGINX_CONF || {
    echo "ERROR: Failed to change the port in the nginx configuration file $FILE_NGINX_CONF."
    exit 1
}

# copy the nginx configuration file
echo "Copying nginx configuration file $FILE_NGINX_CONF to $FILE_NGINX_CONF_STORE..."
cp -rf $FILE_NGINX_CONF $FILE_NGINX_CONF_STORE || {
    echo "ERROR: Failed to copy the nginx configuration file."
    exit 1
}

