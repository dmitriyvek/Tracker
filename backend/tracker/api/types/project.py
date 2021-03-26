import graphene
from sqlalchemy import and_

from graphene.types import ResolveInfo

from tracker.api.connections import CustomPageInfo, validate_connection_params, create_connection_from_record_list
from tracker.api.connections.roles import RoleConnection
from tracker.api.dataloaders import get_generic_loader
from tracker.api.types.role import RoleType
from tracker.api.services.projects import get_project_node
from tracker.api.services.roles import ROLES_REQUIRED_FIELDS, get_projects_role_list
from tracker.api.wrappers import login_required
from tracker.db.schema import roles_table


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
    async def get_node(cls, info: ResolveInfo, project_id):
        project_id = int(project_id)
        user_id = info.context['request']['user_id']
        db = info.context['request'].app['db']

        # may be used by different resolvers
        info.context['request']['project_id'] = project_id

        record = await get_project_node(db, info, project_id, user_id)
        record = cls(**record)

        return record

    @staticmethod
    async def resolve_role_list(
        parent, info: ResolveInfo, **connection_params
    ):
        # if called from node
        if project_id := info.context['request'].get('project_id'):
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

        # if called from connection
        else:
            # initialize data loader
            if not info.context.get('loader'):
                db = info.context['request'].app['db']
                max_fetch_number = info.context['request'].app.\
                    get('config', {}).\
                    get('max_fetch_number')

                connection_params = validate_connection_params(
                    connection_params,
                    RoleType,
                    max_fetch_number,
                    nested_connection=True
                )

                info.context['loader'] = get_generic_loader(
                    db,
                    roles_table,
                    'project_id',
                    connection_params,
                    [roles_table.c.id, *ROLES_REQUIRED_FIELDS]
                )()

            record_list = await info.context['loader'].load(parent['id'])

        return create_connection_from_record_list(
            record_list,
            connection_params,
            RoleConnection,
            RoleType,
            CustomPageInfo
        )
