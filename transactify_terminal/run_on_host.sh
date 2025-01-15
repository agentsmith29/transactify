export MAIN_DB="cashless_terminal1_1"
export PGPASSWORD="PASSWORD"
export PGUSER="USER"
export PGHOST="192.168.1.190"
export DJANGO_SUPERUSER_PASSWORD="admin"
export DJANGO_SUPERUSER_USERNAME="admin"
export DJANGO_SUPERUSER_EMAIL="$DJANGO_SUPERUSER_PASSWORD@$DJANGO_SUPERUSER_USERNAME.com"


#psql -h $PGHOST -U $PGUSER -p 5432 -d 'postgres' -c "DROP DATABASE IF EXISTS \"$MAIN_DB\";"
#psql -h $PGHOST  -U $PGUSER -p 5432 -d 'postgres' -c "CREATE DATABASE \"$MAIN_DB\" OWNER \"$PGUSER\";"

export RUN_SERVER="false" # To avoid code being run during migration
# Run migration
#python manage.py makemigrations
#python manage.py migrate
#python manage.py createsuperuser --noinput
export RUN_SERVER="true"
daphne -b 0.0.0.0 -p 8881 transactify_terminal.asgi:application