import graphene
from sqlalchemy import and_

from graphene.types import ResolveInfo
from tracker.api.types.role import RoleType
from tracker.api.services.projects import get_project_node, get_total_count_of_user_projects
from tracker.api.wrappers import login_required
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
    # role_list = graphene.List(
    #     RoleType,
    #     required=True,
    #     description='List of all roles in given project'
    # )
    my_role = graphene.Field(
        RoleType,
        required=True,
        description='Role of the current user in given project'
    )

    class Meta:
        interfaces = (graphene.relay.Node, )

    @classmethod
    @login_required
    async def get_node(cls, info, project_id):
        project_id = int(project_id)
        user_id = info.context['request']['user_id']
        db = info.context['request'].app['db']

        record = await get_project_node(db, info, project_id, user_id)
        record = cls(**record)

        return record


class ProjectConnection(graphene.relay.Connection):
    total_count = graphene.Int(
        required=True,
        description='Total number of user\'s projects'
    )

    class Meta:
        node = ProjectType

    def resolve_total_count(parent, info: ResolveInfo):
        db = info.context['request'].app['db']
        user_id = info.context['request']['user_id']

        total_count = get_total_count_of_user_projects(db, user_id)
        return total_count
