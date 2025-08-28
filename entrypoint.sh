#!/bin/bash

# Wait for postgres
echo "Waiting for PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U nutricoach; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for redis
echo "Waiting for Redis..."
while ! redis-cli -h redis ping; do
  sleep 1
done
echo "Redis is ready!"

# Initialize database
echo "Initializing database..."
python -c "
from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    try:
        db.create_all()
        print('Database tables created successfully')
    except Exception as e:
        print(f'Error creating tables: {e}')
        exit(1)
"

# Start the application
echo "Starting NutriCoach application..."
exec python -u app.py