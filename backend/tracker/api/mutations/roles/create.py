import graphene
from graphql_relay import from_global_id

from ..base import BaseMutationPayload
from tracker.api.schemas.roles import RoleCreationSchema
from tracker.api.services import validate_input
from tracker.api.services.roles import (
    RoleData, RoleResponseData,
    check_if_role_exists, create_role, check_if_user_is_project_manager
)
from tracker.api.status_codes import StatusEnum
from tracker.api.types import RoleType
from tracker.api.wrappers import login_required
from tracker.db.schema import UserRoleEnum


class RoleCreationStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value

    @property
    def description(self):
        if self == RoleCreationStatus.SUCCESS:
            return 'Successfully created new role'
        elif self == RoleCreationStatus.BAD_REQUEST:
            return 'Role creation failed: bad request'
        elif self == RoleCreationStatus.ENPROCESSABLE_ENTITY:
            return 'Role creation failed: invalid input'


class RoleCreationInput(graphene.InputObjectType):
    role = graphene.Field(
        graphene.Enum.from_enum(UserRoleEnum),
        required=True
    )
    user_id = graphene.ID(required=False)
    project_id = graphene.ID(required=False)


class RoleCreationPayload(graphene.ObjectType):
    record = graphene.Field(RoleType, required=True)
    record_id = graphene.Int(required=True)
    status = graphene.Field(RoleCreationStatus, required=True)


class RoleCreation(BaseMutationPayload, graphene.Mutation):
    '''Entity for creation new role on a project'''

    class Arguments:
        input = RoleCreationInput(required=True)

    role_creation_payload = graphene.Field(
        RoleCreationPayload, required=True)

    @staticmethod
    @login_required
    async def mutate(parent, info, input):
        app = info.context['request'].app
        data = validate_input(input, RoleCreationSchema)

        data['assign_by'] = info.context['request']['user_id']
        data['project_id'] = int(from_global_id(data['project_id'])[1])
        await check_if_user_is_project_manager(
            db=app['db'],
            user_id=data['assign_by'],
            project_id=data['project_id']
        )
        data['user_id'] = int(from_global_id(data['user_id'])[1])

        await check_if_role_exists(app['db'], data)

        role = await create_role(app['db'], data)

        return RoleCreation(
            role_creation_payload=RoleCreationPayload(
                record=role,
                record_id=role['id'],
                status=RoleCreationStatus.SUCCESS,
            )
        )
