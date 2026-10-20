#!/usr/bin/env bash
# Render build: install, collect static files, migrate, and load any
# missing course content (seed_course never overwrites admin edits).
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed_course
