#!/bin/sh
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 run:flask_app