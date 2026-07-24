#!/bin/sh
# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for database to be ready..."

# Run a python snippet that checks DB connection using sqlalchemy/psycopg2
python -c "
import sys
import time
from sqlalchemy import create_engine
from app.core.config import settings

url = settings.DATABASE_URL.replace('+asyncpg', '')
max_retries = 30
for i in range(max_retries):
    try:
        # Try to connect using the synchronous driver for check
        engine = create_engine(url)
        with engine.connect() as conn:
            print('Database is ready and accepting connections!')
            sys.exit(0)
    except Exception as e:
        print(f'Database connection attempt {i+1}/{max_retries} failed, retrying in 1s...')
        time.sleep(1)
print('Database could not be reached after multiple retries.')
sys.exit(1)
"

echo "Database is ready. Executing Alembic migrations..."
alembic upgrade head

echo "Migrations completed successfully. Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
