from functools import partial

from aiohttp import web

from tracker.api.errors import APIException
from tracker.api.services.auth import decode_auth_token


class GraphQLErrorMiddleware:

    def on_error(self, error, logger, debug: bool):
        if not isinstance(error, APIException):
            if debug:
                logger.exception('GraphQL error middleware')
            else:
                logger.error(error)

            raise APIException('Internal server error.', status=500)

        raise error

    def resolve(self, next, root, info, **args):
        return next(root, info, **args).catch(
            partial(
                self.on_error,
                logger=info.context['request'].app['logger'],
                debug=info.context['request'].app['config']['debug']
            )
        )


@web.middleware
async def auth_middleware(request, handler):
    auth_header = request.headers.get('Authorization')
    auth_token = ''

    if auth_header:
        auth_credentials = auth_header.split(' ')
        if auth_credentials[0] == 'Bearer':
            auth_token = auth_credentials[1]

    if auth_token:
        payload = await decode_auth_token(
            request.app['db'],
            request.app['config'],
            auth_token
        )
        if payload:
            request['user_id'] = payload['sub']

    # request['user_id'] = 1
    return await handler(request)


@web.middleware
async def request_logging_middleware(request, handler):
    logger = request.app['logger'].bind(request_log=True)

    request_query = await request.json() if request.content_length else {}

    log_message = '{method}:{path_qs}:{query}:{user_id}:{user_ip}'.format(
        method=request.method,
        path_qs=request.path_qs,
        query=request_query,
        user_id=request.get('user_id', 0),
        user_ip=request.remote,
    )
    logger.info(log_message)

    return await handler(request)
