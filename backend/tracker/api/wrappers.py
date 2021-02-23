from functools import wraps
from typing import Awaitable
from types import FunctionType

from aiohttp.web import HTTPUnauthorized
from aiohttp.web_urldispatcher import View


def login_required(func: FunctionType) -> Awaitable:
    '''Decorator that checks user\'s authorization. Using only for View subclass methods'''

    @wraps(func)
    async def wrapped_func(cls, *args, **kwargs):

        if not isinstance(cls, View):
            raise TypeError(
                'Function that uses login_required should be the method of aiohttp.web_urldispatcher.View subclass')

        user_id = cls.request.get('user_id')
        if user_id:
            return await func(*args, **kwargs)

        else:
            error_message = {
                'status': 'fail',
                'message': 'Provide a valid auth credentials.'
            }
            raise HTTPUnauthorized(reason=error_message,
                                   content_type='application/json')

    return wrapped_func
