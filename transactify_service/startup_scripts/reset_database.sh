# Ensure required environment variables are set
if [ -z "$DJANGO_DB_HOST" ] || [ -z "$DJANGO_DB_USER" ] || [ -z "$DJANGO_DB_PASSWORD" ] || [ -z "$SERVICE_NAME" ]; then
    echo "Error: One or more required environment variables are not set."
    echo "Ensure DJANGO_DB_HOST, DJANGO_DB_USER, DJANGO_DB_PASSWORD, and DJANGO_DB_NAME are set."
    exit 1
fi

# Database-specific settings
PGHOST=$DJANGO_DB_HOST
PGUSER=$DJANGO_DB_USER
PGPASSWORD=$DJANGO_DB_PASSWORD
PGPORT=${DJANGO_DB_PORT:-5432} # Default PostgreSQL port if not set

MAIN_DB="$CONTAINER_NAME"   # Main Django database
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