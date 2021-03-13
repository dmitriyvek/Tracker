import graphene
from graphql import ResolveInfo

from tracker.api.types import ProjectType
from tracker.api.wrappers import login_required
from tracker.api.services.projects import get_user_projects


class ProjectListQuery(graphene.ObjectType):
    records = graphene.List(
        ProjectType,
        description='List of all projects in which the currently loged user participates',
        required=True
    )

    @login_required
    async def resolve_records(parent, info: ResolveInfo):
        db = info.context['request'].app['db']
        user_id = info.context['request'].get('user_id')

        records = await get_user_projects(db, user_id)
        return records

# query = select([projects_table.c.title, roles_table.c.id]).select_from(projects_table.join(roles_table, roles_table.c.project_id == projects_table.c.id)).where(projects_table.c.id == 1)

# query = union(projects_table.select().with_only_columns([projects_table.c.id]).where(projects_table.c.id == 2), roles_table.select().with_only_columns([roles_table.c.user_id]).where(roles_table.c.project_id == 2))

# query = union(projects_table.select().with_only_columns([literal_column('1').label('num'), projects_table.c.id]).where(projects_table.c.id == 2), roles_table.select(
# ).with_only_columns([literal_column('2').label('num'), roles_table.c.user_id]).where(roles_table.c.project_id == 2)).order_by('num')
