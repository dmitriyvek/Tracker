release: tracker-migrate upgrade head
web: bin/start-nginx gunicorn -c ./backend/config/gunicorn_heroku_config.py tracker.api.app:wsgi --log-file -