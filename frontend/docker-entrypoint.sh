#!/bin/sh

htpasswd -cb /etc/nginx/.htpasswd $AUTH_USER $AUTH_PASS

exec "$@"
