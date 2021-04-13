import graphene
from sqlalchemy import and_

from graphene.types import ResolveInfo

from tracker.api.connections import (
    CustomPageInfo, create_connection_from_record_list,
    validate_connection_params
)
from tracker.api.dataloaders import get_generic_loader
from tracker.api.scalars.projects import Description, Title
from tracker.api.schemas.projects import TitleDuplicationCheckSchema
from tracker.api.services import validate_input
from tracker.api.services.projects import (
    check_title_duplication,
    get_project_node,
    get_total_count_of_user_projects,
)
from tracker.api.services.roles import (
    ROLES_REQUIRED_FIELDS, get_projects_role_list
)
from tracker.api.types.role import RoleType, RoleConnection
from tracker.api.wrappers import login_required
from tracker.db.schema import roles_table


class ProjectType(graphene.ObjectType):
    title = Title(
        required=True,
        description='A title of a project',
    )
    description = Description(
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
            if not info.context.get('role_list_loader'):
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

                info.context['role_list_loader'] = get_generic_loader(
                    db=db,
                    table=roles_table,
                    attr='project_id',
                    connection_params=connection_params,
                    nested_connection=True,
                    required_fields=[roles_table.c.id, *ROLES_REQUIRED_FIELDS]
                )()

            record_list = await info.context['role_list_loader'].load(parent['id'])

        return create_connection_from_record_list(
            record_list,
            connection_params,
            RoleConnection,
            RoleType,
            CustomPageInfo
        )


class ProjectConnection(graphene.relay.Connection):
    total_count = graphene.Int(
        required=True,
        description='Total number of user\'s projects'
    )

    class Meta:
        node = ProjectType

    @staticmethod
    def resolve_total_count(parent, info: ResolveInfo):
        db = info.context['request'].app['db']
        user_id = info.context['request']['user_id']

        total_count = get_total_count_of_user_projects(db, user_id)
        return total_count


class ProjectDuplicationChecksType(graphene.ObjectType):
    title = graphene.Boolean(
        required=True,
        description='Does user already have a project with given title',
        title=Title(required=True)
    )

    @staticmethod
    @login_required
    async def resolve_title(parent, info: ResolveInfo, title):
        db = info.context['request'].app['db']
        user_id = info.context['request']['user_id']
        data = {'title': title}
        validate_input(data, TitleDuplicationCheckSchema)

        is_existed = await check_title_duplication(
            db, user_id=user_id, title=title
        )
        return is_existed