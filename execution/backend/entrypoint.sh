#!/bin/sh

# Run Alembic migrations before starting the server (with timeout to avoid blocking startup)
echo "Running database migrations..."
if timeout 30 alembic upgrade head 2>&1; then
    echo "Migrations complete."
else
    echo "WARNING: Migration failed or timed out, starting server anyway."
fi

echo "Starting uvicorn..."
exec "$@"
