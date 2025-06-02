#!/bin/sh

# Wait for Postgres to be ready (adjust host/port if needed)

echo "Postgres is up - running init_db.py"
python3 src/init_db.py

echo "Starting uvicorn"
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
