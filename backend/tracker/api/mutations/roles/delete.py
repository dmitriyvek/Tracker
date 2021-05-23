import graphene
from graphene.types import ResolveInfo
from graphql_relay import from_global_id

from ..base import BaseMutationPayload
from tracker.api.schemas.roles import RoleDeletionSchema
from tracker.api.services import validate_input
from tracker.api.services.roles import (
    check_user_priviliges_for_role_deletion,
    delete_role_by_id
)
from tracker.api.status_codes import StatusEnum
from tracker.api.wrappers import login_required


class RoleDeletionStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value
    FORBIDDEN = StatusEnum.FORBIDDEN.value

    @property
    def description(self):
        if self == RoleDeletionStatus.SUCCESS:
            return 'Successfully deleted given role.'
        elif self == RoleDeletionStatus.BAD_REQUEST:
            return 'Role deletion failed: bad request.'
        elif self == RoleDeletionStatus.ENPROCESSABLE_ENTITY:
            return 'Role deletion failed: invalid input.'
        elif self == RoleDeletionStatus.FORBIDDEN:
            return 'Role role deletion failed: '\
                'you do not have enough privileges.'


class RoleDeletionInput(graphene.InputObjectType):
    role_id = graphene.ID(required=True)


class RoleDeletionPayload(graphene.ObjectType):
    status = graphene.Field(RoleDeletionStatus, required=True)


class RoleDeletion(BaseMutationPayload, graphene.Mutation):
    '''
    Entity for role deletion.
    You must be a project\' creator for deletion project manager.
    And be a project manager to delete another roles.
    Nobody can delete role of project\'s creator.
    '''

    class Arguments:
        input = RoleDeletionInput(required=True)

    role_deletion_payload = graphene.Field(
        RoleDeletionPayload, required=True)

    @staticmethod
    @login_required
    async def mutate(parent, info: ResolveInfo, input: RoleDeletionInput):
        app = info.context['request'].app
        data = validate_input(input, RoleDeletionSchema)

        role_id = int(from_global_id(data['role_id'])[1])
        deletion_by_id = info.context['request']['user_id']

        await check_user_priviliges_for_role_deletion(
            db=app['db'],
            role_id=role_id,
            deletion_by_id=deletion_by_id
        )
        await delete_role_by_id(db=app['db'], role_id=role_id)

        return RoleDeletion(
            role_deletion_payload=RoleDeletionPayload(
                status=RoleDeletionStatus.SUCCESS,
            )
        )
