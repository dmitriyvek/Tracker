import warnings

import aiohttp_cors
import aiosmtplib
from aiohttp import web
from jinja2 import Environment, PackageLoader, select_autoescape

from tracker.api.middleware import auth_middleware, request_logging_middleware
from tracker.api.views import gqil_view, gql_view
from tracker.utils import setup_db, setup_logger, close_logger
from tracker.utils.settings import MAIN_CONFIG


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
        cors_options['https://studio.apollographql.com'] = \
            cors_resourse_options

        resource = cors.add(app.router.add_resource('/graphql'), cors_options)
        cors.add(resource.add_route('POST', gql_view))
        cors.add(resource.add_route('GET', gql_view))
        resource = cors.add(app.router.add_resource('/graphql/'), cors_options)
        cors.add(resource.add_route('POST', gql_view))
        cors.add(resource.add_route('GET', gql_view))

    else:
        resource = app.router.add_resource('/graphql/')
        resource.add_route('POST', gql_view)
        resource.add_route('GET', gql_view)
        resource = app.router.add_resource('/graphql')
        resource.add_route('POST', gql_view)
        resource.add_route('GET', gql_view)


def create_app(config: dict = MAIN_CONFIG) -> web.Application:
    app = web.Application(
        middlewares=[auth_middleware, request_logging_middleware, ])

    app['config'] = config

    if app['config']['debug']:
        warnings.warn(
            'App is running in debug mode.', category=RuntimeWarning
        )

    app['logger'] = setup_logger(
        app['config']['log_level'],
        app['config']['error_log_file_path'],
        app['config']['info_log_file_path'],
        app['config']['request_info_log_file_path'],
        app['config']['debug']
    )

    env = Environment(
        loader=PackageLoader('tracker', 'api/templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    app['jinja_env'] = env

    cors = aiohttp_cors.setup(app)

    # connect to db on startup and disconnect on shut down
    app.cleanup_ctx.append(setup_db)

    app.on_shutdown.append(close_logger)

    init_routes(app, cors)

    # inti smpt client
    config = app['config']
    smtp_client = aiosmtplib.SMTP(
        hostname=config['mail_server'],
        port=config['mail_port'],
        username=config['mail_username'],
        password=config['mail_password'],
        use_tls=config['mail_use_ssl'],
        timeout=config['mail_timeout'],
    )

    host = config['domain_name']
    schema = config['url_schema']
    domain = 'http://localhost:3000' \
        if host == 'localhost' or host == '127.0.0.1' else \
        f'{schema}://{host}'

    app['smtp_client'] = smtp_client
    app['config']['to_smtp_domain'] = domain

    return app


async def wsgi():
    return create_app()
