from functools import partial

import aiohttp_cors
from aiohttp import web

from tracker.utils import get_config, setup_db, setup_logger, close_logger
from tracker.api.views import gqil_view, gql_view
from tracker.api.middleware import auth_middleware, request_logging_middleware


def init_routes(app, cors):
    # app.router.add_route('GET', '/graphql', gql_view, name='graphql')
    # app.router.add_route('POST', '/graphql', gql_view, name='graphql')

    resource = cors.add(app.router.add_resource("/graphql"))
    cors.add(
        resource.add_route('POST', gql_view), {
            "http://localhost:3000": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers='*',
                allow_headers='*',
                max_age=3600,
            )
        }
    )
    cors.add(
        resource.add_route('GET', gql_view), {
            "http://localhost:3000": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers='*',
                allow_headers='*',
                max_age=3600,
            )
        }
    )

    if app['config']['debug']:
        app.router.add_route('GET', '/graphiql', gqil_view, name='graphiql')
        app.router.add_route('POST', '/graphiql', gqil_view, name='graphiql')


def create_app() -> web.Application:
    app = web.Application(
        middlewares=[auth_middleware, request_logging_middleware, ])
    app['config'] = get_config()

    app['logger'] = setup_logger(
        app['config']['log_level'],
        app['config']['error_log_file_path'],
        app['config']['info_log_file_path'],
        app['config']['request_info_log_file_path'],
        app['config']['debug']
    )

    cors = aiohttp_cors.setup(app)

    # connect to db on startup and disconnect on shut down
    app.cleanup_ctx.append(setup_db)

    app.on_shutdown.append(close_logger)

    init_routes(app, cors)

    return app
