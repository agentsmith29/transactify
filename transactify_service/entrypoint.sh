#!/bin/bash


# Ensure the necessary environment variables are set
# export DJANGO_SETTINGS_MODULE=terminal.settings

PYTHON_EXEC=python
MANAGE_PY="python manage.py"

# check if REMIGRATE is set or available
if [ -z "$REMIGRATE" ]; then
    echo "REMIGRATE is not set. Setting REMIGRATE to false..."
    REMIGRATE=false
fi
# if statement to check if REMIGRATE is set to true
chmod +x make_store_db_migration.sh
if [ "$REMIGRATE" = "true" ]; then
    echo "Remigrating the database..."
    # run make migrations
    ./make_store_db_migration.sh
fi

#$MANAGE_PY migrate --noinput || {
#    echo "ERROR: Failed to migrate"
#    exit 1
#}

# Step 6: Collect static files
#echo "Collecting static files..."
rm -rf /app/static/*
echo "Copying staticfiles to /static..."
ls -l /app/static/

cp -r /app/staticfiles/* /app/static/ || {
    echo "ERROR: Failed copy staticfiles to /static"
    exit 1
}

#$MANAGE_PY collectstatic --noinput || {
#    echo "ERROR: Failed to collect static files."
#    exit 1
#}

ls -l /app/static/assets/js/
ls -l /app/staticfiles/assets/js/
#ls -l /app/staticfiles/assets/js/

export PYTHONUNBUFFERED=1
# Step 7: Start the server
echo "Starting the Django development server..."
daphne -b 0.0.0.0 -p ${DJANGO_WEB_PORT} transactify_service.asgi:application 
exit 0