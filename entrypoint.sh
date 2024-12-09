#!/bin/bash


# Ensure the necessary environment variables are set
export DJANGO_SETTINGS_MODULE=terminal.settings

PYTHON_EXEC=python
MANAGE_PY="python manage.py"

# rename /app/cashlessui/store to /app/cashlessui/$DJANGO_DB_NAME
#mv /app/cashlessui/store /app/cashlessui/$DJANGO_DB_NAME
#
#chmod +x make_migrations.sh
#chmod +x make_user_db_migration.sh
#chmod +x make_store_db_migration.sh
#chmod +x convert_svg_png.py
# run make migrations
#./make_user_db_migration.sh
#./make_store_db_migration.sh

#$MANAGE_PY migrate --noinput || {
#    echo "ERROR: Failed to migrate"
#    exit 1
#}

# Step 6: Collect static files
#echo "Collecting static files..."
#$MANAGE_PY collectstatic --noinput || {
#    echo "ERROR: Failed to collect static files."
#    exit 1
#}

python /app/static/tools/convert_svg_png.py


# Step 7: Start the server
echo "Starting the Django development server..."
daphne -b 0.0.0.0 -p ${PORT} terminal.asgi:application 
exit 0