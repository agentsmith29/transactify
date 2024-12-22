#!/bin/bash


# Ensure the necessary environment variables are set
#export DJANGO_SETTINGS_MODULE=terminal.settings

PYTHON_EXEC=python
MANAGE_PY="python manage.py"


chmod +x make_terminal_db_migration.sh
#./make_terminal_db_migration.sh


python /app/static/tools/convert_svg_png.py


# Step 7: Start the server
echo "Starting the Django development server..."
daphne -b 0.0.0.0 -p ${PORT} transactify_terminal.asgi:application 
exit 0