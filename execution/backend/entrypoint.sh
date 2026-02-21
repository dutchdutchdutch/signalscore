#!/bin/sh

# Run Alembic migrations before starting the server
echo "Running database migrations..."
if alembic upgrade head; then
    echo "Migrations complete."
else
    echo "WARNING: Migration failed, starting server anyway."
fi

echo "Starting uvicorn..."
exec "$@"
