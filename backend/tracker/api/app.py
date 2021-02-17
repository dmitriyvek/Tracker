from functools import partial

from aiohttp import web

from tracker.utils import get_config, setup_db, setup_logger, close_logger


def create_app(argv=None) -> web.Application:
    app = web.Application()
    app['config'] = get_config(argv)

    app['logger'] = setup_logger(app['config']['log_level'])
    app['logger'].debug('TATA')

    # connect to db on startup and disconnect on shut down
    app.cleanup_ctx.append(setup_db)

    app.on_shutdown.append(close_logger)

    return app
