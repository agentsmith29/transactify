#!/bin/bash

# Wait for the database to be ready

echo "Ensuring the database exists..."
#PGPASSWORD=$DJANGO_DB_PASSWORD psql -h $DJANGO_DB_HOST -U $DJANGO_DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$DJANGO_DB_NAME'" | grep -q 1 || \
PGPASSWORD=$DJANGO_DB_PASSWORD psql -h $DJANGO_DB_HOST -U $DJANGO_DB_USER -c "CREATE DATABASE $DJANGO_DB_NAME"
echo "Database exists now."

# Run database migrations
echo "Applying migrations..."
#mkdir -p /app/static
#python manage.py findstatic	
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
#python manage.py makemigrations store
#python manage.py migrate store
#python manage.py collectstatic --noinput



# Start the Django server
# Start the daphne server
#echo "Starting Daphne server..."
daphne -b 0.0.0.0 -p ${DJANGO_WEB_PORT} cashlessui.asgi:application 
echo "Starting Django server on ${DJANGO_WEB_HOST}:${DJANGO_WEB_PORT}..."
# sleep in order to wait for the database to be ready
#sleep 10
#python manage.py runserver #0.0.0.0:${DJANGO_WEB_PORT}
