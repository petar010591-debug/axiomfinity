#!/bin/sh
set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8001}"

sed "s|__BACKEND_URL__|${BACKEND_URL}|g" \
    /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

echo "Starting nginx with backend=${BACKEND_URL}"
nginx -g 'daemon off;'
