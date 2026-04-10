#!/usr/bin/env bash
set -o errexit

echo "Starting Django deploy bootstrap"
if [ -d "/var/data" ]; then
	export MEDIA_ROOT="${MEDIA_ROOT:-/var/data/media}"
fi

if [ "${MEDIA_ROOT:-}" = "/var/data" ] || [ "${MEDIA_ROOT:-}" = "/var/data/" ]; then
	export MEDIA_ROOT="/var/data/media"
fi

if [ -n "${MEDIA_ROOT:-}" ] && [[ "${MEDIA_ROOT}" == /var/data* ]] && [ ! -d "/var/data" ]; then
	echo "MEDIA_ROOT targets /var/data but disk is not mounted. Falling back to ./media"
	export MEDIA_ROOT="./media"
fi

mkdir -p "${MEDIA_ROOT:-./media}"

# Django uses MEDIA_ROOT directly; a local ./media symlink is optional.
# On some platforms, replacing ./media may fail and should not crash startup.
if [ "${MEDIA_ROOT:-./media}" != "./media" ]; then
	if [ ! -e "./media" ]; then
		ln -s "${MEDIA_ROOT}" ./media || echo "Warning: could not create ./media symlink; continuing"
	fi
fi

echo "Using MEDIA_ROOT=${MEDIA_ROOT:-./media}"

wait_for_database() {
	if [ -z "${DATABASE_URL:-}" ]; then
		echo "DATABASE_URL not set. Proceeding with DB settings from environment/defaults."
		return 0
	fi

	echo "Checking database DNS and connectivity..."
	python - <<'PY'
import os
import socket
import sys
from urllib.parse import urlparse

import psycopg2

database_url = os.environ.get("DATABASE_URL", "").strip()
if not database_url:
    sys.exit(0)

parsed = urlparse(database_url)
host = parsed.hostname
port = parsed.port or 5432

if not host:
    print("DATABASE_URL is set but host could not be parsed", flush=True)
    sys.exit(2)

try:
    socket.getaddrinfo(host, port)
except OSError as exc:
    print(f"DNS lookup failed for {host}:{port} -> {exc}", flush=True)
    sys.exit(1)

try:
    conn = psycopg2.connect(database_url, connect_timeout=5)
    conn.close()
except Exception as exc:
    print(f"Database connect failed: {exc}", flush=True)
    sys.exit(1)

print("Database connectivity check passed", flush=True)
PY
}

max_attempts=12
attempt=1
until wait_for_database; do
	echo "Database not ready (attempt ${attempt}/${max_attempts})."
	if [ "${attempt}" -ge "${max_attempts}" ]; then
		echo "Database was not reachable after ${max_attempts} attempts. Exiting."
		exit 1
	fi
	attempt=$((attempt + 1))
	sleep 5
done

python manage.py migrate --noinput
# Seeding is best-effort and should not block app boot.
python manage.py seed_render_content || echo "Warning: seed_render_content failed; continuing"
python manage.py collectstatic --noinput

exec gunicorn blog.wsgi:application --bind 0.0.0.0:${PORT:-10000}