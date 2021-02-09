from aiohttp import web

from tracker.utils import get_config


def init_app(argv=None) -> web.Application:
    app = web.Application()
    app['config'] = get_config(argv)

    return app
