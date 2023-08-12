#!/bin/sh
poetry run python3 manage.py makemigrations --no-input
poetry run python3 manage.py migrate --no-input
exec "$@"
