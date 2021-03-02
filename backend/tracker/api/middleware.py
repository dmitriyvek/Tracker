from functools import partial

from aiohttp import web

from tracker.api.errors import APIException
from tracker.api.services import decode_token


class GraphQLErrorMiddleware(object):

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
        payload = await decode_token(
            request.app['db'],
            request.app['config'],
            auth_token
        )
        if payload:
            request['user_id'] = payload['sub']

    return await handler(request)
