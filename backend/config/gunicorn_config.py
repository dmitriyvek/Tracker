import os

from dotenv import load_dotenv


load_dotenv()

command = '/home/www/code/tracker/backend/env/bin/gunicorn'
pythonpath = '/home/www/code/tracker/backend'
bind = '{host}:{port}'.format(
    host=os.getenv('api_host'), port=os.getenv('api_port'))
workers = 3
worker_class = 'aiohttp.GunicornWebWorker'
user = 'www'
limit_request_fields = 32000
limit_request_field_size = 0
raw_env = 'gunicorn=True'
loglevel = 'info'
accesslog = '/home/www/code/tracker/backend/log/gunicorn/access.log'
acceslogformat = "%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog = '/home/www/code/tracker/backend/log/gunicorn/error.log'
