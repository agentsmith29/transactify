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
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Install Django 5 and Python dependencies
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

ENV APP_DIR /app/webapp
ENV CONFIG_FILE="$APP_DIR/configs/config.yaml"

COPY .env                       /app/.env
COPY ./staticfiles              /app/staticfiles
COPY ./common                   /app/common


# Expose the application port
EXPOSE 8000
WORKDIR $APP_DIR

# ----------------- NEW CODE -----------------

COPY ./transactify_service ${APP_DIR}

RUN chmod +x $APP_DIR/entrypoint.sh 
RUN chmod +x $APP_DIR/entrypoint.tests.sh

# Run migrations and start the Django development server
ENTRYPOINT ["/app/webapp/entrypoint.sh"]