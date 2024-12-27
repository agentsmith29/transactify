#!/bin/bash


# Ensure the necessary environment variables are set
# export DJANGO_SETTINGS_MODULE=terminal.settings

PYTHON_EXEC=python
MANAGE_PY="python manage.py"

#chmod +x make_migrations.sh
chmod +x make_store_db_migration.sh
# run make migrations
./make_store_db_migration.sh

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

# python /app/static/tools/convert_svg_png.py



export PYTHONUNBUFFERED=1
$MANAGE_PY test store/tests/