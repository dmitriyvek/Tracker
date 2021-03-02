import graphene

from tracker.db.schema import User as UserTable


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
        description='Timestamp user\'s registration',
    )

    class Meta:
        interfaces = (graphene.relay.Node, )

    @classmethod
    async def get_node(cls, info, id):
        id = int(id)
        app = info.context['request'].app
        query = UserTable.select().\
            with_only_columns([
                UserTable.c.id,
                UserTable.c.username,
                UserTable.c.email,
                UserTable.c.registered_at
            ]).\
            where(UserTable.c.id == id)
        user = await app['db'].fetchrow(query)
        user = cls(**user)
        return user
