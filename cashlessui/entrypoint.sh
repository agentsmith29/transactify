#!/bin/bash


# Ensure the necessary environment variables are set
export DJANGO_SETTINGS_MODULE=cashlessui.settings

PYTHON_EXEC=python
MANAGE_PY="python manage.py"

# rename /app/cashlessui/store to /app/cashlessui/$DJANGO_DB_NAME
#mv /app/cashlessui/store /app/cashlessui/$DJANGO_DB_NAME

chmod +x make_migrations.sh
chmod +x make_user_db_migration.sh
chmod +x make_store_db_migration..sh
# run make migrations
#./make_user_db_migration.sh
#./make_store_db_migration.sh
#./make_migrations.sh

# Step 6: Collect static files
echo "Collecting static files..."
$MANAGE_PY collectstatic --noinput || {
    echo "ERROR: Failed to collect static files."
    exit 1
}

# Step 7: Start the server
echo "Starting the Django development server..."
daphne -b 0.0.0.0 -p ${DJANGO_WEB_PORT} cashlessui.asgi:application 
exit 0


# old
# Wait for the database to be ready

echo "Ensuring the database exists..."
#PGPASSWORD=$DJANGO_DB_PASSWORD psql -h $DJANGO_DB_HOST -U $DJANGO_DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$DJANGO_DB_NAME'" | grep -q 1 || \
PGPASSWORD=$DJANGO_DB_PASSWORD psql -h $DJANGO_DB_HOST -U $DJANGO_DB_USER -c "CREATE DATABASE $DJANGO_DB_NAME"
echo "Database exists now."

# Run database migrations
echo "Applying migrations..."
#mkdir -p /app/static
echo "flushing database"
python manage.py migrate auth zero --database=USER
python manage.py migrate auth zero --database=default
#python manage.py findstatic	
python manage.py flush --database=USER --noinput 
python manage.py flush --database=default --noinput

echo "collecting static files"
python manage.py collectstatic --noinput 

echo "making migrations"
python manage.py makemigrations 
python manage.py makemigrations store

echo "migrating"

python manage.py migrate admin --database=USER 
python manage.py migrate auth --database=USER
python manage.py migrate contenttypes --database=USER
python manage.py migrate --database=USER 
python manage.py migrate store --database=default
python manage.py migrate --database=default


#python manage.py collectstatic --noinput
echo "Migrations applied. Adding superuser..."
python manage.py createsuperuser --username=joe --email=joe@example.com --noinput




# Start the Django server
# Start the daphne server
#echo "Starting Daphne server..."
daphne -b 0.0.0.0 -p ${DJANGO_WEB_PORT} cashlessui.asgi:application 
echo "Starting Django server on ${DJANGO_WEB_HOST}:${DJANGO_WEB_PORT}..."
# sleep in order to wait for the database to be ready
#sleep 10
#python manage.py runserver #0.0.0.0:${DJANGO_WEB_PORT}
