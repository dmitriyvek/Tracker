import graphene

from ..base import BaseMutationPayload
from tracker.api.status_codes import StatusEnum
from tracker.api.services.auth import create_blacklist_token
from tracker.api.wrappers import login_required


class LogoutStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    UNAUTHORIZED = StatusEnum.UNAUTHORIZED.value

    @property
    def description(self):
        if self == LogoutStatus.SUCCESS:
            return 'Successfully logged out'
        elif self == LogoutStatus.UNAUTHORIZED:
            return 'Logout faild: no auth token is provided'


class LogoutPayload(graphene.ObjectType):
    status = graphene.Field(LogoutStatus, required=True)


class Logout(BaseMutationPayload, graphene.Mutation):
    '''Logout user (make auth token blacklisted)'''

    logout_payload = graphene.Field(LogoutPayload, required=True)

    @staticmethod
    @login_required
    async def mutate(parent, info):
        db = info.context['request'].app['db']
        auth_token = info.context['request'].\
            headers.get('Authorization').split(' ')[1]

        await create_blacklist_token(db, token=auth_token)

        return Logout(
            logout_payload=LogoutPayload(status=LogoutStatus.SUCCESS)
        )
