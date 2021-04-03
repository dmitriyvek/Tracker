from functools import partial

import aiohttp_cors
from aiohttp import web

from tracker.utils import get_config, setup_db, setup_logger, close_logger
from tracker.api.views import gqil_view, gql_view
from tracker.api.middleware import auth_middleware, request_logging_middleware


def init_routes(app, cors):
    cors_resourse_options = aiohttp_cors.ResourceOptions(
        allow_methods=['POST', 'GET', 'OPTIONS'],
        allow_credentials=True,
        expose_headers=(),
        allow_headers=('Content-Type', 'Authorization'),
        max_age=3600,
    )
    cors_options = {
        'http://localhost:3000': cors_resourse_options,
    }

    if app['config']['debug']:
        app.router.add_route('GET', '/graphiql', gqil_view, name='graphiql')
        app.router.add_route('POST', '/graphiql', gqil_view, name='graphiql')
        # add cors for apollo sudio
        cors_options['https://studio.apollographql.com'] = cors_resourse_options

    resource = cors.add(app.router.add_resource("/graphql"), cors_options)
    cors.add(resource.add_route('POST', gql_view))
    cors.add(resource.add_route('GET', gql_view))


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
