#!/usr/bin/env bash
set -o errexit

echo "Starting Django deploy bootstrap"
mkdir -p "${MEDIA_ROOT:-./media}"
python manage.py migrate --noinput
python manage.py seed_render_content
python manage.py collectstatic --noinput

exec gunicorn blog.wsgi:application --bind 0.0.0.0:${PORT:-10000}