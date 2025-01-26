set -e

# get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $DIR/functions.sh

# Paths to Python and manage.py
PYTHON_EXEC=python
MANAGE_PY="python manage.py"


echo_inf "Applying migrations for application $APP_NAME ..."
$MANAGE_PY migrate $APP_NAME || {
    echo_err "Failed to apply $APP_NAME migrations for the default database. Exiting."
    exit 1
} 
echo_ok "Migrations for $APP_NAME applied successfully."

# Step 3: Run migrations for the default database
echo_inf "Applying migrations for the default database..."
$MANAGE_PY migrate || {
    echo_err "Failed to apply migrations for the default database. Exiting."
    exit 1
}
echo_ok "Migrations applied successfully."


echo_inf "Creating a superuser for the USER database (if not exists)..."
$MANAGE_PY create_or_update_superuser  || {
    echo_err "ERROR: Failed to create superuser $ADMIN_USER. Exiting"
    exit 1
}
echo_ok "Superuser $ADMIN_USER created successfully."


