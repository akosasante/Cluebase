#!/bin/sh

echo "Waiting for postgres..."

DATABASE_PORT=${DATABASE_PORT:-5432}
while ! nc -z postgres $DATABASE_PORT; do
  sleep 0.1
done

echo "Postgres started ✅"
echo "Waiting for redis..."


REDIS_PORT=${REDIS_PORT:-6379}
while ! nc -z redis $REDIS_PORT; do
  sleep 0.1
done

echo "Redis started ✅"

sleep 3

echo "PostgreSQL and Redis started, now running flask service"

python --version
pip --version
cat requirements.txt

python run.py run -h 0.0.0.0
