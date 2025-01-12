# Base image optimized for Raspberry Pi
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies for Python, GPIO, and PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libgpiod-dev \
    libpq-dev \
    postgresql-client \
    ntpdate \
    curl \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
#RUN ntpdate pool.ntp.org
# Install Django 5 and Python dependencies
COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY ./cashless_terminal/entrypoint.sh /app/entrypoint.sh 
COPY ./cashless_terminal/ /app/
COPY ./static /app/static
COPY ./shared /app/shared

#COPY ./entrypoint.sh /app/entrypoint.sh
#COPY ./make_migrations.sh /app/make_migrations.sh
#COPY ./make_user_db_migration.sh /app/make_user_db_migration.sh
#COPY ./make_store_db_migration.sh /app/make_store_db_migration.sh

RUN chmod +x /app/entrypoint.sh 
#RUN chmod +x /app/make_migrations.sh 
#RUN chmod +x /app/make_user_db_migration.sh
#RUN chmod +x /app/make_store_db_migration.sh


# Expose the application port
EXPOSE 8000

# Run migrations and start the Django development server
ENTRYPOINT ["/app/entrypoint.sh"]