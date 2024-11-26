# Ensure required environment variables are set
if [ -z "$DJANGO_DB_HOST" ] || [ -z "$DJANGO_DB_USER" ] || [ -z "$DJANGO_DB_PASSWORD" ] || [ -z "$DJANGO_DB_NAME" ]; then
    echo "Error: One or more required environment variables are not set."
    echo "Ensure DJANGO_DB_HOST, DJANGO_DB_USER, DJANGO_DB_PASSWORD, and DJANGO_DB_NAME are set."
    exit 1
fi

# Database-specific settings
PGHOST=$DJANGO_DB_HOST
PGUSER=$DJANGO_DB_USER
PGPASSWORD=$DJANGO_DB_PASSWORD
PGPORT=${DJANGO_DB_PORT:-5432} # Default PostgreSQL port if not set

USER_DB="USER" # Name of the USER database
MAIN_DB="$DJANGO_DB_NAME" # Main Django database
TEMP_DB="postgres"  # Temporary database to connect to during database operations


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


set -e

# Paths to Python and manage.py
PYTHON_EXEC=python
MANAGE_PY="python manage.py"

echo "Starting Django setup script..."


#$MANAGE_PY makemigrations store || {
#    echo "ERROR: Failed to generate migrations store."
#    exit 1
#}


#echo "Generating migrations..."
#$MANAGE_PY makemigrations || {
#    echo "ERROR: Failed to generate migrations."
#    exit 1
#}


# Step 4: Run migrations for the USER database
echo "Applying migrations for the default database..."
$MANAGE_PY migrate store --database=default || {
    echo "ERROR: Failed to apply store migrations for the default database."
    exit 1
} 


# Step 3: Run migrations for the default database
echo "Applying migrations for the default database..."
$MANAGE_PY migrate --database=default || {
    echo "ERROR: Failed to apply migrations for the default database."
    exit 1
}
