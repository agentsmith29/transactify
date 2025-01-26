#!/bin/bash
set -e
export RUN_SERVER="false" # To avoid code being run during migration

echo "Sourcing the entrypoint_template.sh from ${APP_DIR}/../entrypoint_template.sh"
source "${APP_DIR}/../entrypoint_template.sh"



export RUN_SERVER="true"
export INIT_DATA=0
echo "Starting the server..."
DJANGO_WEB_PORT=$(python $CONFIG_FILE --getvar "webservice.SERVICE_WEB_PORT")
daphne -b 0.0.0.0 -p ${DJANGO_WEB_PORT} transactify_service.asgi:application 
exit 0