#!/bin/bash
set -e

echo "Sourcing the entrypoint_template.sh from ${APP_DIR}/../entrypoint_template.sh"
source ${APP_DIR}/../common/scripts/entrypoint_template.sh

echo "Applying migrations for application $APP_NAME ..."
python ${APP_DIR}/../common/scripts/convert_svg_png.py "${APP_DIR}/../staticfiles/icons/svg" "${APP_DIR}/../static/icons/png"

# Step 7: Start the server
echo "Starting the Django development server..."
DJANGO_WEB_PORT=$(python ${APP_DIR}/config/Config.py $CONFIG_FILE --getvar "webservice.SERVICE_WEB_PORT")
DAPHNE_DEBUG=1 daphne -b 0.0.0.0 -p ${DJANGO_WEB_PORT} transactify_terminal.asgi:application 
exit 0