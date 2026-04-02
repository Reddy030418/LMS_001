# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Ensure production dependencies are available
RUN pip install gunicorn psycopg2-binary channels daphne django-axes django-auditlog

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Start daphne server for ASGI/WebSockets
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "anu_lms.asgi:application"]
