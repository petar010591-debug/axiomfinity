#!/bin/sh
# Replace BACKEND_URL in nginx config, then start nginx
BACKEND_URL="${BACKEND_URL:-http://localhost:8001}"
PORT="${PORT:-3000}"

sed "s|__BACKEND_URL__|${BACKEND_URL}|g; s|__PORT__|${PORT}|g" \
    /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "Nginx starting: port=${PORT}, backend=${BACKEND_URL}"
exec nginx -g 'daemon off;'
