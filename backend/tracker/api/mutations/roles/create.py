import graphene
from graphene.types import ResolveInfo
from graphql_relay import from_global_id

from ..base import BaseMutationPayload
from tracker.api.scalars.auth import Email
from tracker.api.scalars.roles import EmailList
from tracker.api.schemas.roles import RoleCreationSchema
from tracker.api.services import send_email_factory, validate_input
from tracker.api.services.roles import (
    RolesData,
    check_if_user_is_project_manager,
    get_emails_of_duplicated_roles, get_rid_of_duplications,
    send_role_confirmation_email,
)
from tracker.api.status_codes import StatusEnum
from tracker.api.wrappers import login_required
from tracker.db.schema import UserRoleEnum


class RoleCreationStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value
    FORBIDDEN = StatusEnum.FORBIDDEN.value

    @property
    def description(self):
        if self == RoleCreationStatus.SUCCESS:
            return 'Successfully created new role'
        elif self == RoleCreationStatus.BAD_REQUEST:
            return 'Role creation failed: bad request'
        elif self == RoleCreationStatus.ENPROCESSABLE_ENTITY:
            return 'Role creation failed: invalid input'
        elif self == RoleCreationStatus.FORBIDDEN:
            return 'Role creation failed: '\
                'you must be a manager of a given project'


class RoleCreationInput(graphene.InputObjectType):
    role = graphene.Field(
        graphene.Enum.from_enum(UserRoleEnum),
        required=True
    )
    email_list = EmailList(
        graphene.NonNull(Email),
        required=True
    )
    project_id = graphene.ID(required=False)


class RoleCreationPayload(graphene.ObjectType):
    duplicated_email_list = EmailList(
        Email,
        description='A list contains emails of duplicated roles.',
        required=True,
    )
    status = graphene.Field(RoleCreationStatus, required=True)
    error_list = graphene.List(
        graphene.String,
        description='A list of errors that occurred when sending emails.',
        required=True
    )


class RoleListCreation(BaseMutationPayload, graphene.Mutation):
    '''
    Entity for creation new roles for users
    with given emails on a project.
    '''

    class Arguments:
        input = RoleCreationInput(required=True)

    role_creation_payload = graphene.Field(
        RoleCreationPayload, required=True)

    @staticmethod
    @login_required
    async def mutate(parent, info: ResolveInfo, input):
        app = info.context['request'].app
        data = validate_input(input, RoleCreationSchema)
        data['email_list'] = list(set(data['email_list']))
        print(data['email_list'])

        data['assign_by'] = info.context['request']['user_id']
        data['project_id'] = int(from_global_id(data['project_id'])[1])
        data['title'] = await check_if_user_is_project_manager(
            db=app['db'],
            user_id=data['assign_by'],
            project_id=data['project_id']
        )
        data = RolesData(**data)

        duplicated_email_list = await get_emails_of_duplicated_roles(
            app['db'], data
        )
        data = get_rid_of_duplications(data, duplicated_email_list)
        send_conf_email = send_email_factory(app=app)(
            send_role_confirmation_email
        )
        error_list = await send_conf_email(app=app, data=data)

        return RoleListCreation(
            role_creation_payload=RoleCreationPayload(
                error_list=error_list,
                duplicated_email_list=duplicated_email_list,
                status=RoleCreationStatus.SUCCESS,
            )
        )
