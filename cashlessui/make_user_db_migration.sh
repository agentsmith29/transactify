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

# Drop USER database if it exists
execute_psql "DROP DATABASE IF EXISTS \"$USER_DB\";"

# Create USER database
execute_psql "CREATE DATABASE \"$USER_DB\" OWNER \"$PGUSER\";"

echo "Databases $USER_DB have been reset successfully."


set -e

# Paths to Python and manage.py
PYTHON_EXEC=python
MANAGE_PY="python manage.py"

echo "Starting Django setup script..."

#$MANAGE_PY makemigrations cashlessui || {
#    echo "ERROR: Failed to generate migrations cashlessui."
#    exit 1
#}


#$MANAGE_PY makemigrations store || {
#    echo "ERROR: Failed to generate migrations store."
#    exit 1
#}



echo "Applying cashlessui migrations for the USER database..."
$MANAGE_PY migrate cashlessui --database=USER || {
    echo "ERROR: Failed to apply cashlessui migrations for the USER database."
    exit 1
} 

echo "Applying cashlessui migrations for the USER database..."
$MANAGE_PY migrate store --database=USER || {
    echo "ERROR: Failed to apply cashlessui migrations for the USER database."
    exit 1
} 

# Step 4: Run migrations for the USER database
echo "Applying migrations for the USER database..."
$MANAGE_PY migrate --database=USER || {
    echo "ERROR: Failed to apply migrations for the USER database."
    exit 1
}

# Step 5: Create a superuser for the USER database (if needed)
echo "Creating a superuser for the USER database (if not exists)..."
export DJANGO_SUPERUSER_PASSWORD="admin"
export DJANGO_SUPERUSER_USERNAME="admin"
export DJANGO_SUPERUSER_EMAIL="test@me.com"
$MANAGE_PY createsuperuser --database=USER --noinput || {
    echo "ERROR: Failed to create superuser for the USER database."
    echo "To create manually, run: python manage.py createsuperuser --database=USER"
}

