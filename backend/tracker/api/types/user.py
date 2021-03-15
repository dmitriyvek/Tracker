import graphene
from sqlalchemy import and_

from tracker.api.wrappers import login_required
from tracker.api.services.users import get_user_by_id
from tracker.db.schema import users_table


class UserType(graphene.ObjectType):
    '''
    A user is an individual's account on current api that can take part in projects.
    '''
    username = graphene.String(
        required=True,
        description='A username of user',
    )
    email = graphene.String(
        required=True,
        description='A email of user',
    )
    registered_at = graphene.DateTime(
        required=True,
        description='User registration timestamp',
    )

    class Meta:
        interfaces = (graphene.relay.Node, )

    @classmethod
    @login_required
    async def get_node(cls, info, user_id):
        user_id = int(user_id)
        db = info.context['request'].app['db']

        record = await get_user_by_id(db, user_id)
        record = cls(**record)

        return record
