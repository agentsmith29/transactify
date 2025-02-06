set -e

# get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $DIR/functions.sh

# Paths to Python and manage.py
PYTHON_EXEC=python
MANAGE_PY="python manage.py"

# echo_inf "Make all migrations"
# $MANAGE_PY makemigrations || {
#     echo_err "Failed to apply migrations for the default database. Exiting."
#     exit 1
# }
# echo_ok "All migrations made successfully."

# Iterate through each application name
for APP_NAME in $APP_NAMES; do
    # echo "Applying migrations for application $APP_NAME ..."
    # $MANAGE_PY makemigrations $APP_NAME || {
    #     echo "Failed to apply $APP_NAME migrations for the default database. Exiting."
    #     exit 1
    # }
    # echo "Migrations for $APP_NAME applied successfully."

    echo "Applying migrations for application $APP_NAME ..."
    $MANAGE_PY migrate $APP_NAME || {
        echo "Failed to apply $APP_NAME migrations for the default database. Exiting."
        exit 1
    }
    echo "Migrations for $APP_NAME applied successfully."
done


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


