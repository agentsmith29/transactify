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

MAIN_DB="$SERVICE_NAME" # Main Django database
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
# Step 4: Run migrations for the USER database
echo "Applying migrations for the default database..."
#$MANAGE_PY migrate transactify_service || {
#    echo "ERROR: Failed to apply store migrations for the default database."
#    exit 1
#} 

$MANAGE_PY migrate store || {
    echo "ERROR: Failed to apply store migrations for the default database."
    exit 1
} 

# Step 3: Run migrations for the default database
echo "Applying migrations for the default database..."
$MANAGE_PY migrate || {
    echo "ERROR: Failed to apply migrations for the default database."
    exit 1
}


# Step 5: Create a superuser for the USER database (if needed)
echo "Creating a superuser for the USER database (if not exists)..."
export DJANGO_SUPERUSER_PASSWORD="admin"
export DJANGO_SUPERUSER_USERNAME="admin"
export DJANGO_SUPERUSER_EMAIL="test@me.com"
$MANAGE_PY createsuperuser --noinput || {
    echo "ERROR: Failed to create superuser for the USER database."
    echo "To create manually, run: python manage.py createsuperuser"
}
