from functools import wraps
from typing import Awaitable
from types import FunctionType

from graphene.types import ResolveInfo

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum


def login_required(func: FunctionType) -> Awaitable:
    '''Decorator that checks user\'s authorization'''

    @wraps(func)
    async def wrapped_func(parent, info: ResolveInfo, *args, **kwargs):

        if not isinstance(info, ResolveInfo):
            raise TypeError(
                'login_required decorator should be \
                used only with graphene resolvers'
            )

        user_id = info.context['request'].get('user_id')
        if user_id:
            return await func(parent, info, *args, **kwargs)

        else:
            raise APIException('Provide a valid auth token.',
                               status=StatusEnum.UNAUTHORIZED.name)

    return wrapped_func
