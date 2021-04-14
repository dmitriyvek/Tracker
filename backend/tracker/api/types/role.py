import graphene
from graphql import ResolveInfo

from tracker.api.dataloaders import get_generic_loader
from tracker.api.services.users import USERS_REQUIRED_FIELDS
from tracker.api.services.roles import get_total_count_of_roles_in_project
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
            )()

        record = await info.context['user_loader'].load(parent['user_id'])
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
        user_id = info.context['request']['user_id']

        # make sense only in project's node execution
        project_id = info.context['request']['project_id']

        total_count = get_total_count_of_roles_in_project(db, project_id)
        return total_count
