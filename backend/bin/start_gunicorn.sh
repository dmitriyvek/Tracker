#!/bin/bash
source /home/www/code/tracker/backend/env/bin/activate
source /home/www/code/tracker/backend/.env
tracker-migrate upgrade head
exec gunicorn -c "/home/www/code/tracker/backend/config/gunicorn_config.py" tracker.api.app:wsgi