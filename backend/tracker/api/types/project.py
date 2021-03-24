import graphene
from sqlalchemy import and_

from graphene.types import ResolveInfo

from tracker.api.connections import CustomPageInfo, validate_connection_params, create_connection_from_records_list
from tracker.api.connections.roles import RoleConnection
from tracker.api.types.role import RoleType
from tracker.api.services.projects import get_project_node
from tracker.api.services.roles import get_projects_role_list
from tracker.api.wrappers import login_required


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
    role_list = graphene.relay.ConnectionField(
        RoleConnection,
        required=True,
        description='List of all roles in given project'
    )
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

        # may be used by different resolvers
        info.context['request']['project_id'] = project_id

        record = await get_project_node(db, info, project_id, user_id)
        record = cls(**record)

        return record

    @staticmethod
    async def resolve_role_list(parent, info, **connection_params):
        project_id = info.context['request']['project_id']
        db = info.context['request'].app['db']
        max_fetch_number = info.context['request'].app.\
            get('config', {}).\
            get('max_fetch_number')

        connection_params = validate_connection_params(
            connection_params,
            RoleType,
            max_fetch_number
        )
        record_list = await get_projects_role_list(
            db, info, project_id, connection_params
        )

        return create_connection_from_records_list(
            record_list,
            connection_params,
            RoleConnection,
            RoleType,
            CustomPageInfo
        )
