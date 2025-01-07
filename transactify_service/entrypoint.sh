#!/bin/bash
export RUN_SERVER="false" # To avoid code being run during migration
export APP_NAME="store"
source /app/entrypoint_template.sh

#export HOSTNAME=$(hostname)
#DOCKERINFO=$(curl -s --unix-socket /run/docker.sock http://docker/containers/$HOSTNAME/json)
# echo "DOCKERINFO: $DOCKERINFO"
#export CONTAINER_NAME=$(echo "$DOCKERINFO" | jq -r '.Name' | sed 's|/||')
#export PYTHONUNBUFFERED=1
# Step 7: Start the server
export RUN_SERVER="true"
echo "Starting the server..."
daphne -b 0.0.0.0 -p ${DJANGO_WEB_PORT} transactify_service.asgi:application 
exit 0