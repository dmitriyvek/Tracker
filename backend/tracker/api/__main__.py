from aiohttp import web

from tracker.api.app import create_app


def main():
    app = create_app()
    config = app['config']
    if app['api_port']:
        web.run_app(app, host=config['api_host'], port=config['api_port'])
    else:
        web.run_app(app, host=config['api_host'])


if __name__ == '__main__':
    main()
