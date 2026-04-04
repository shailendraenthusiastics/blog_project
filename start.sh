#!/usr/bin/env bash
set -o errexit

echo "Starting Django deploy bootstrap"
if [ -d "/var/data" ]; then
	export MEDIA_ROOT="${MEDIA_ROOT:-/var/data/media}"
fi

mkdir -p "${MEDIA_ROOT:-./media}"

if [ "${MEDIA_ROOT:-./media}" != "./media" ]; then
	rm -rf ./media
	ln -s "${MEDIA_ROOT}" ./media
fi

echo "Using MEDIA_ROOT=${MEDIA_ROOT:-./media}"
python manage.py migrate --noinput
python manage.py seed_render_content
python manage.py collectstatic --noinput

exec gunicorn blog.wsgi:application --bind 0.0.0.0:${PORT:-10000}