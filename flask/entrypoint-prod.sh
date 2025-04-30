#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do
  sleep 0.1
done

echo "Postgres started ✅"
echo "Waiting for redis..."

while ! nc -z redis 6379; do
  sleep 0.1
done

echo "Redis started ✅"

sleep 3

echo "PostgreSQL and Redis started, now running flask service"

gunicorn -b 0.0.0.0:5000 run:app
