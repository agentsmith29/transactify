#!/bin/bash
set -e

echo "Sourcing the entrypoint_template.sh from ${APP_DIR}/../entrypoint_template.sh"
source ${APP_DIR}/../common/scripts/entrypoint_template.sh

# Step 7: Start the server
echo "Starting the Django development server..."
DJANGO_WEB_PORT=$(python ${APP_DIR}/config/Config.py $CONFIG_FILE --getvar "webservice.SERVICE_WEB_PORT")
DAPHNE_DEBUG=1 daphne -b 0.0.0.0 -p ${DJANGO_WEB_PORT} transactify_service.asgi:application 
exit 0