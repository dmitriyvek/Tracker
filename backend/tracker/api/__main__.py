import sys

from aiohttp import web

from tracker.api.app import create_app


def main(argv):
    app = create_app()
    config = app['config']
    web.run_app(app, host=config['api_address'], port=config['api_port'])


if __name__ == '__main__':
    main(sys.argv[1:])
