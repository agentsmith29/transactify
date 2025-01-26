#!/bin/bash
export APP_DIR="."
export CONFIG_FILE="./configs/terminal_config.yaml"
./entrypoint.sh

exit 1


export  "INIT_DATA"=0
if [ "$INIT_DATA" = "1" ]; then
    psql -h $PGHOST -U $PGUSER -p 5432 -d 'postgres' -c "DROP DATABASE IF EXISTS \"$MAIN_DB\";"
    psql -h $PGHOST  -U $PGUSER -p 5432 -d 'postgres' -c "CREATE DATABASE \"$MAIN_DB\" OWNER \"$PGUSER\";"

    export RUN_SERVER="false" # To avoid code being run during migration
    # Run migration
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser --noinput
fi

export RUN_SERVER="true"
daphne -b 0.0.0.0 -p 8881 transactify_terminal.asgi:application