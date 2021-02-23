from aiohttp import web

from tracker.api.services import decode_token


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)

    except web.HTTPException as ex:
        return web.json_response(data=ex.reason, status=ex.status_code)

    except Exception as ex:
        request.app['logger'].exception('Error middleware')
        data = {
            'status': 'fail',
        }
        return web.json_response(data=data, status=web.HTTPInternalServerError.status_code)


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
        request['user_id'] = payload['sub']

    return await handler(request)
