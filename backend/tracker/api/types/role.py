import graphene
from graphql import ResolveInfo
from graphql_relay import from_global_id

from tracker.api.dataloaders import get_generic_loader
from tracker.api.services import validate_input
from tracker.api.services.users import USERS_REQUIRED_FIELDS
from tracker.api.services.roles import (
    check_if_user_is_project_manager,
    check_user_role_duplication,
    get_total_count_of_roles_in_project,
    get_role_node,
)
from tracker.api.schemas.roles import RoleDuplicationCheckSchema
from tracker.api.wrappers import login_required
from tracker.db.schema import users_table


class RoleType(graphene.ObjectType):
    role = graphene.String(
        required=True,
        description='A name of given role',
    )
    user_id = graphene.Int(
        required=True,
        description='The id of user which has this role',
    )
    project_id = graphene.Int(
        required=True,
        description='The id of the project to which this role is associated',
    )
    assign_by = graphene.Int(
        required=True,
        description='The id of user which created this role',
    )
    assign_at = graphene.DateTime(
        required=True,
        description='Role creation timestamp',
    )

    user = graphene.Field(
        'tracker.api.types.user.UserType',
        required=True,
        description='User linked with this role'
    )

    class Meta:
        interfaces = (graphene.relay.Node, )

    @classmethod
    @login_required
    async def get_node(cls, info: ResolveInfo, role_id):
        role_id = int(role_id)
        user_id = info.context['request']['user_id']
        db = info.context['request'].app['db']

        # may be used by different resolvers
        info.context['request']['role_id'] = role_id

        record = await get_role_node(db, info, role_id, user_id)
        record = cls(**record)

        return record

    @staticmethod
    async def resolve_user(parent, info: ResolveInfo):
        if not info.context.get('user_loader'):
            db = info.context['request'].app['db']

            info.context['user_loader'] = get_generic_loader(
                db=db,
                table=users_table,
                attr='id',
                connection_params=None,
                nested_connection=False,
                required_fields=USERS_REQUIRED_FIELDS,
                many=False,
            )()

        # parent is RoleType in node; parent is dict in connection (list)
        user_id = parent.user_id if isinstance(
            parent, RoleType) else parent['user_id']

        record = await info.context['user_loader'].load(user_id)
        return record


class RoleConnection(graphene.relay.Connection):
    total_count = graphene.Int(
        required=True,
        description='Total number of roles in project'
    )

    class Meta:
        node = RoleType

    @staticmethod
    def resolve_total_count(parent, info: ResolveInfo):
        db = info.context['request'].app['db']

        # make sense only in project's node execution
        project_id = info.context['request']['project_id']

        total_count = get_total_count_of_roles_in_project(db, project_id)
        return total_count


class RoleDuplicationChecksInput(graphene.InputObjectType):
    user_id = graphene.ID(required=False)
    project_id = graphene.ID(required=False)


class RoleDuplicationChecksType(graphene.ObjectType):
    role = graphene.Boolean(
        required=True,
        description='Does user already take part in given project',
        input=RoleDuplicationChecksInput(required=True)
    )

    @staticmethod
    @login_required
    async def resolve_role(parent, info: ResolveInfo, input):
        app = info.context['request'].app
        data = validate_input(input, RoleDuplicationCheckSchema)

        call_by = info.context['request']['user_id']
        project_id = int(from_global_id(data['project_id'])[1])
        await check_if_user_is_project_manager(
            db=app['db'],
            user_id=call_by,
            project_id=project_id
        )
        user_id = int(from_global_id(data['user_id'])[1])

        is_existed = await check_user_role_duplication(
            db=app['db'],
            user_id=user_id,
            project_id=project_id
        )

        return is_existed
