import graphene
from sqlalchemy import and_

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
    async def get_node(cls, info, id):
        id = int(id)
        app = info.context['request'].app
        query = users_table.select().\
            with_only_columns([
                users_table.c.id,
                users_table.c.username,
                users_table.c.email,
                users_table.c.registered_at
            ]).\
            where(and_(
                users_table.c.id == id,
                users_table.c.is_deleted.is_(False)
            ))
        user = await app['db'].fetchrow(query)
        user = cls(**user)
        return user
