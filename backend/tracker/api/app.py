from functools import partial

from aiohttp import web

from tracker.api.handlers import HANDLERS
from tracker.utils import get_config, setup_db, setup_logger, close_logger
from tracker.api.middleware import error_middleware, auth_middleware


def create_app(argv=None) -> web.Application:
    app = web.Application(middlewares=[error_middleware, auth_middleware])
    app['config'] = get_config(argv)

    app['logger'] = setup_logger(
        app['config']['log_level'],
        app['config']['error_log_file_path'],
        app['config']['info_log_file_path'],
        app['config']['debug']
    )

    # connect to db on startup and disconnect on shut down
    app.cleanup_ctx.append(setup_db)

    app.on_shutdown.append(close_logger)

    for handler in HANDLERS:
        app['logger'].debug(
            f'Registering handler {handler} as {handler.URL_PATH}')
        app.router.add_route('*', handler.URL_PATH, handler)

    return app
