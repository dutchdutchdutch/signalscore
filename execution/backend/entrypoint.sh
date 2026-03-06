#!/bin/sh

# Run Alembic migrations before starting the server (with timeout to avoid blocking startup)
echo "Running database migrations..."
if timeout 30 alembic upgrade head 2>&1; then
    echo "Migrations complete."
else
    echo "WARNING: Migration failed or timed out."
    echo "Attempting to stamp current state so future migrations can run..."
    if timeout 10 alembic stamp head 2>&1; then
        echo "Database stamped at current head."
    else
        echo "WARNING: Could not stamp database, starting server anyway."
    fi
fi

echo "Starting uvicorn..."
exec "$@"
