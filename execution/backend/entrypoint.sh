#!/bin/sh
set -e

# Run Alembic migrations before starting the server
echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn..."
exec "$@"
