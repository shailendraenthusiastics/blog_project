#!/usr/bin/env bash
set -o errexit

echo "Starting Django deploy bootstrap"
python manage.py migrate --noinput
python manage.py seed_blogs_if_empty
python manage.py shell -c "from api.models import Blog; print('BLOG_COUNT_AT_STARTUP', Blog.objects.filter(is_active=True).count())"
python manage.py collectstatic --noinput

exec gunicorn blog.wsgi:application --bind 0.0.0.0:${PORT:-10000}