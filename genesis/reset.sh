#!/bin/sh

rm lab/migrations/00*.py
echo "migrations removed"
dropdb genesis
echo "db removed"
createdb -E utf8 -O genesis genesis
echo "db created"
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata ./fixtures/*.json

