#!/bin/bash
set -e

echo "Starting Uno Tracker Backend..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 1
  echo "Waiting for database..."
done
echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI application..."
exec "$@"
