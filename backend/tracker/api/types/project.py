import graphene
from sqlalchemy import and_

from tracker.db.schema import projects_table


class ProjectType(graphene.ObjectType):
    title = graphene.String(
        required=True,
        description='A title of a project',
    )
    description = graphene.String(
        required=False,
        description='A description of a project',
    )
    created_at = graphene.DateTime(
        required=True,
        description='Project creation timestamp',
    )

    class Meta:
        interfaces = (graphene.relay.Node, )

    @classmethod
    async def get_node(cls, info, id):
        id = int(id)
        app = info.context['request'].app
        query = projects_table.select().\
            with_only_columns([
                projects_table.c.id,
                projects_table.c.title,
                projects_table.c.description,
                projects_table.c.created_at
            ]).\
            where(and_(
                projects_table.c.id == id,
                projects_table.c.is_deleted.is_(False)
            ))
        user = await app['db'].fetchrow(query)
        user = cls(**user)
        return user
