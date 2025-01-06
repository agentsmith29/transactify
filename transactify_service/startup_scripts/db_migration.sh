set -e

# Paths to Python and manage.py
PYTHON_EXEC=python
MANAGE_PY="python manage.py"

echo "Starting Django setup script..."
echo "Applying migrations for the default database..."
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

export DJANGO_SUPERUSER_PASSWORD=$ADMIN_PASSWORD
export DJANGO_SUPERUSER_USERNAME=$ADMIN_USER 
export DJANGO_SUPERUSER_EMAIL=$ADMIN_EMAIL 
echo "Creating a superuser for the USER database (if not exists)..."
$MANAGE_PY create_or_update_superuser  || {
    echo "ERROR: Failed to create superuser $ADMIN_USER."
    echo "To create manually, run: python manage.py createsuperuser"
    exit 1
}
echo "Superuser $ADMIN_USER created successfully."


