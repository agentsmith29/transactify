#!/bin/bash
export INIT_HARDWARE=0
export APP_NAME="terminal"
export DB_RESET=$(python ./config/Config.py $TERMINAL_CONFIG_FILE --getvar "database.DB_RESET")
export REMIGRATE=$(python ./config/Config.py $TERMINAL_CONFIG_FILE --getvar "database.REMIGRATE")

source ${APP_DIR}/entrypoint_template.sh

python ${APP_DIR}/static/tools/convert_svg_png.py

# Step 7: Start the server
export INIT_HARDWARE=1
echo "Starting the Django development server..."
DJANGO_WEB_PORT=$(python ./config/Config.py $TERMINAL_CONFIG_FILE --getvar "webservice.SERVICE_WEB_PORT")
DAPHNE_DEBUG=1 daphne -b 0.0.0.0 -p ${DJANGO_WEB_PORT} transactify_terminal.asgi:application 
exit 0