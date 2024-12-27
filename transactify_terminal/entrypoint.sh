#!/bin/bash


# Ensure the necessary environment variables are set
#export DJANGO_SETTINGS_MODULE=terminal.settings

PYTHON_EXEC=python
MANAGE_PY="python manage.py"

# check if REMIGRATE is set or available
if [ -z "$REMIGRATE" ]; then
    echo "REMIGRATE is not set. Setting REMIGRATE to false..."
    REMIGRATE=false
fi

chmod +x make_terminal_db_migration.sh
if [ "$REMIGRATE" = "true" ]; then
    echo "Remigrating the database..."
    ./make_terminal_db_migration.sh
fi



python /app/static/tools/convert_svg_png.py


# Step 7: Start the server
echo "Starting the Django development server..."
daphne -b 0.0.0.0 -p ${PORT} transactify_terminal.asgi:application 
exit 0