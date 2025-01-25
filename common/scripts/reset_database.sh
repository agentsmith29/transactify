# Ensure required environment variables are set
PGHOST=$(python ./config/Config.py $CONFIG_FILE --getvar "database.HOST")
PGUSER=$(python ./config/Config.py $CONFIG_FILE --getvar "database.USER")
PGPASSWORD=$(python ./config/Config.py $CONFIG_FILE --getvar "database.PASSWORD")
PGPORT=$(python ./config/Config.py $CONFIG_FILE --getvar "database.PORT")
SERVICE_NAME=$(python ./config/Config.py $CONFIG_FILE --getvar "webservice.SERVICE_NAME")

MAIN_DB=$(python ./config/Config.py $CONFIG_FILE --getvar "database.NAME")

if [ -z "$PGHOST" ] || [ -z "$PGUSER" ] || [ -z "$PGPASSWORD" ] || [ -z "$SERVICE_NAME" ] || [ -z "$MAIN_DB" ]; then
    echo "Error: One or more required environment variables are not set."
    echo "Ensure PGHOST, PGUSER, PGPASSWORD, SERVICE_NAME and MAIN_DB are set."
    exit 1
fi

TEMP_DB="postgres"          # Temporary database to connect to during database operations


echo "Attempting to reset databases on $PGHOST as $PGUSER..."

execute_psql() {
    echo "Running: $1"
    PGPASSWORD=$PGPASSWORD psql -h $PGHOST -U $PGUSER -p $PGPORT -d "$TEMP_DB" -c "$1"
}

# Drop MAIN database if it exists
execute_psql "DROP DATABASE IF EXISTS \"$MAIN_DB\";"

# Create MAIN database
execute_psql "CREATE DATABASE \"$MAIN_DB\" OWNER \"$PGUSER\";"

echo "Databases $MAIN_DB have been reset successfully."