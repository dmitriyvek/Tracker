from aiohttp import web


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
    return await handler(request)
