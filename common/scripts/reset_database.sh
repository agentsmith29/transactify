
set -e

# get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $DIR/functions.sh

# Ensure required environment variables are set
PGHOST=$(python ./config/Config.py $CONFIG_FILE --getvar "database.HOST")
PGUSER=$(python ./config/Config.py $CONFIG_FILE --getvar "database.USER")
PGPASSWORD=$(python ./config/Config.py $CONFIG_FILE --getvar "database.PASSWORD")
PGPORT=$(python ./config/Config.py $CONFIG_FILE --getvar "database.PORT")
SERVICE_NAME=$(python ./config/Config.py $CONFIG_FILE --getvar "webservice.SERVICE_NAME")

MAIN_DB=$(python ./config/Config.py $CONFIG_FILE --getvar "database.NAME")

if [ -z "$PGHOST" ] || [ -z "$PGUSER" ] || [ -z "$PGPASSWORD" ] || [ -z "$SERVICE_NAME" ] || [ -z "$MAIN_DB" ]; then
    echo_err "Error: One or more required environment variables are not set."
    echo_err "Ensure PGHOST, PGUSER, PGPASSWORD, SERVICE_NAME and MAIN_DB are set. Exiting"
    exit 1
fi

TEMP_DB="postgres"          # Temporary database to connect to during database operations


echo_inf "Attempting to reset databases on $PGHOST as $PGUSER..."

execute_psql() {
    echo_dbg "Running: $1"
    PGPASSWORD=$PGPASSWORD psql -h $PGHOST -U $PGUSER -p $PGPORT -d "$TEMP_DB" -c "$1" || {
        echo_err "Failed to execute: $1. Exiting."
        exit 1
    }
    echo_ok "Executed: $1"
}

# Drop MAIN database if it exists
execute_psql "DROP DATABASE IF EXISTS \"$MAIN_DB\";"

# Create MAIN database
execute_psql "CREATE DATABASE \"$MAIN_DB\" OWNER \"$PGUSER\";"

echo_ok "Databases $MAIN_DB have been reset successfully."