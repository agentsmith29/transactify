#!/bin/bash
set -e

# get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $DIR/functions.sh

# =====================================================================================================================
export PYTHONUNBUFFERED=1


# the following variable names need to be set
# APP_DIR, CONFIG_FILE
# Ensure the necessary environment variables are set
if [ -z "$APP_DIR" ] || [ -z "$CONFIG_FILE" ]; then
    echo_err "APP_DIR or CONFIG_FILE is not set. Exiting."
    exit 1
else    
    # resolve CONFIG_FILE to absolute path
    CONFIG_FILE=$(relpath "$CONFIG_FILE")
    APP_DIR=$(realpath $APP_DIR)
    echo_inf "APP_DIR is set to $APP_DIR"
    echo_inf "CONFIG_FILE is set to $CONFIG_FILE"
fi

# Check if the configuration file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo_err "Error: Configuration file $CONFIG_FILE does not exist. Exiting."
    exit 1
else
    echo_ok "Configuration file $CONFIG_FILE exists."
fi
cat $CONFIG_FILE

echo_dbg "Reading configuration from $CONFIG_FILE"

# export DJANGO_SETTINGS_MODULE=terminal.settings
export REMIGRATE=$(python ${APP_DIR}/config/Config.py $CONFIG_FILE --getvar "database.REMIGRATE")
export REMIGRATE=$(python ${APP_DIR}/config/Config.py $CONFIG_FILE --getvar "database.REMIGRATE")
export DB_RESET=$(python ${APP_DIR}/config/Config.py $CONFIG_FILE --getvar "database.RESET")
export CONTAINER_NAME=$(python ./config/Config.py $CONFIG_FILE --getvar "container.CONTAINER_NAME")
echo_dbg "Starting container $CONTAINER_NAME (id $HOSTNAME).."


PYTHON_EXEC=python
MANAGE_PY="$PYTHON_EXEC manage.py"

# Directories
export DIR_COMMON="${APP_DIR}/../common"
export DIR_STATIC="${APP_DIR}/../static"
export DIR_SCRIPTS="${DIR_COMMON}/scripts"
export DIR_NGINX="${DIR_COMMON}/nginx"
export DIR_SHARED_CONFIG="/etc/nginx/conf.d"

# Files 
export FILE_NGINX_CONF="$DIR_NGINX/templates/nginx.template.conf"
export FILE_NGINX_CONF_STORE="$DIR_SHARED_CONFIG/nginx.${CONTAINER_NAME}.conf"

# Scripts
export PY_CHANGE_NGINX="$DIR_SCRIPTS/change_nginx.py"
export SH_MAKE_STORE_MIGRATION="$DIR_SCRIPTS/db_migration.sh"
export SH_RESET_DATABSE_SCRIPT="$DIR_SCRIPTS/reset_database.sh"

# Check if running on host: CONTAINER_NAME=host
if [ "$CONTAINER_NAME" = "host" ]; then
    echo_warn "Running on host. Skipping creation of directories..."
else
    echo_dbg "Running on container $CONTAINER_NAME. Creating directories..."
    echo_dbg "Creating directory $DIR_SHARED_CONFIG"
    mkdir -p $DIR_SHARED_CONFIG
fi 

# =====================================================================================================================
# =====================================================================================================================
# Check if all files and directories exist
if [ ! -d "$DIR_STATIC" ]; then
    echo_err "Error: Directory $DIR_STATIC does not exist. Exiting."
    exit 1
fi

if [ ! -d "$DIR_SCRIPTS" ]; then
    echo_err "Error: Directory $DIR_SCRIPTS does not exist. Exiting."
    exit 1
fi

# Check if running on host: CONTAINER_NAME=host
if [ "$CONTAINER_NAME" = "host" ]; then
    echo_warn "Running on host. Skipping nginx configuration checks..."
else
    echo_dbg "Running on container $CONTAINER_NAME. Checking nginx configuration files..."
    echo_dbg "Checking directory $DIR_NGINX"
    if [ ! -d "$DIR_NGINX" ]; then
        echo_err "Error: $DIR_NGINX does not exist. Exiting."
        exit 1
    else
        echo_ok "Directory $DIR_NGINX exists."
    fi

    echo "Checking file $FILE_NGINX_CONF"
    if [ ! -f "$FILE_NGINX_CONF" ]; then
        echo_err "Error: $FILE_NGINX_CONF does not exist. Exiting."
        exit 1
    else
        echo_ok "File $FILE_NGINX_CONF exists."
    fi

    echo "Checking file $PY_CHANGE_NGINX"
    if [ ! -f "$PY_CHANGE_NGINX" ]; then
        echo_err "Error: $PY_CHANGE_NGINX does not exist. Exiting."
        exit 1
    else
        echo_ok "File $PY_CHANGE_NGINX exists."
    fi

    echo "Checking directory $DIR_SHARED_CONFIG"
    if [ ! -d "$DIR_SHARED_CONFIG" ]; then
        echo_err "Error: Directory $DIR_SHARED_CONFIG does not exist. Exiting"
        exit 1
    else
        echo_ok "Directory $DIR_SHARED_CONFIG exists."
    fi
fi 




if [ ! -f "$SH_MAKE_STORE_MIGRATION" ]; then
    echo "Error: Directory $SH_MAKE_STORE_MIGRATION does not exist."
    exit 1
fi



# =====================================================================================================================
# Regmigration of the database, if REMIGRATE is set to true
# =====================================================================================================================
# check if REMIGRATE is set or available

if [ -z "$DB_RESET" ]; then
    echo_inf "DB_RESET is not set. Setting DB_RESET to false..."
    DB_RESET="false"
fi

# if statement to check if REMIGRATE is set to true
echo_inf "Database reset is set to $DB_RESET"
chmod +x $SH_RESET_DATABSE_SCRIPT
if [ "$DB_RESET" = "True" ]; then
    echo_warn "Resetting and remigrating the database with script $SH_RESET_DATABSE_SCRIPT."
    $SH_RESET_DATABSE_SCRIPT || {
        echo_err "Failed to reset and remigrate the database. Exiting."
        exit 1
    }
    REMIGRATE="true"
fi


if [ -z "$REMIGRATE" ]; then
    echo_inf "REMIGRATE is not set. Setting REMIGRATE to false..."
    REMIGRATE="false"
fi

# if statement to check if REMIGRATE is set to true
chmod +x $SH_MAKE_STORE_MIGRATION
echo_inf "Database remigrate is set to $REMIGRATE"
if [ "$REMIGRATE" = "true" ]; then
    echo_warn "Remigrating the database with script $SH_MAKE_STORE_MIGRATION..."
    $SH_MAKE_STORE_MIGRATION || {
        echo_err "Failed to remigrate the database. Exiting."
        exit 1
    }
fi
echo_ok "Database migration completed successfully."



# ========================================
# Collect static files
# ========================================
mkdir -p $DIR_STATIC

echo_inf "Collecting static files..."
#rm -rf  $DIR_STATIC/* || {
#    echo "ERROR: Failed remove files in $DIR_STATIC"
#}

echo_inf "Copying staticfiles to  $DIR_STATIC..."
cp -r ${APP_DIR}/../staticfiles/* $DIR_STATIC/ || {
    echo_err "ERROR: Failed copy staticfiles to $DIR_STATIC. Exiting"
    exit 1
}

$MANAGE_PY collectstatic --noinput || {
    echo_err "ERROR: Failed to collect static files. Exiting"
    exit 1
}

# Check if running on host: CONTAINER_NAME=host
if [ "$CONTAINER_NAME" = "host" ]; then
    echo_warn "Running on host. Skipping nginx configuration adaptation..."
else
    # Alter the nginx configuration file to use the correct port
    # echo_warn "Changing the port in the nginx configuration file using the script $SH_CHANGE_NGINX..."
    # chmod +x $SH_CHANGE_NGINX || {
    #     echo_err "ERROR: Failed to change the port in the nginx configuration file. Exiting."
    #     exit 1
    # }

    echo_inf "Changing the placeholders in the nginx configuration file $FILE_NGINX_CONF..."
    python $PY_CHANGE_NGINX $FILE_NGINX_CONF || {
        echo_err "ERROR: Failed to change the port in the nginx configuration file $FILE_NGINX_CONF. Exiting"
        exit 1
    }
    echo_ok "Nginx configuration file $FILE_NGINX_CONF has been changed successfully."

    # copy the nginx configuration file
    echo_inf "Copying nginx configuration file $FILE_NGINX_CONF to $FILE_NGINX_CONF_STORE..."
    cp -rf $FILE_NGINX_CONF $FILE_NGINX_CONF_STORE || {
        echo_err "ERROR: Failed to copy the nginx configuration file."
        exit 1
    }
    echo_ok "Nginx configuration file $FILE_NGINX_CONF has been copied to $FILE_NGINX_CONF_STORE successfully."
fi
