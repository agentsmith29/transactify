export MAIN_DB="test_db"
export PGPASSWORD="PASSWORD"
export PGUSER="USER"
export PGHOST="192.168.1.190"
export DJANGO_SUPERUSER_PASSWORD="admin"
export DJANGO_SUPERUSER_USERNAME="admin"
export DJANGO_SUPERUSER_EMAIL="$DJANGO_SUPERUSER_PASSWORD@$DJANGO_SUPERUSER_USERNAME.com"

export "RUN_SERVER"="false"
export "INIT_DATA"=1
export "MIGRATE_HISTORICAL"=0
if [ "$INIT_DATA" = "1" ]; then
    echo "Initializing data..."
    export "RUN_SERVER"="false"
    psql -h $PGHOST -U $PGUSER -p 5432 -d 'postgres' -c "DROP DATABASE IF EXISTS \"$MAIN_DB\";"
    psql -h $PGHOST  -U $PGUSER -p 5432 -d 'postgres' -c "CREATE DATABASE \"$MAIN_DB\" OWNER \"$PGUSER\";"

    # Run migration
    python manage.py makemigrations && python manage.py migrate
    # python manage.py createsuperuser --noinput
fi

export "RUN_SERVER"="true"
export PYTHONUNBUFFERED=1
python manage.py test store/tests/
