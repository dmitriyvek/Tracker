import graphene
from graphene.types import ResolveInfo

from ..base import BaseMutationPayload
from tracker.api.scalars.projects import Description, Title
from tracker.api.schemas.projects import ProjectCreationSchema
from tracker.api.services import validate_input
from tracker.api.services.projects import (
    check_if_project_exists, create_project
)
from tracker.api.status_codes import StatusEnum
from tracker.api.types import ProjectType
from tracker.api.wrappers import login_required


class ProjectCreationStatus(graphene.Enum):
    SUCCESS = StatusEnum.SUCCESS.value
    BAD_REQUEST = StatusEnum.BAD_REQUEST.value
    ENPROCESSABLE_ENTITY = StatusEnum.ENPROCESSABLE_ENTITY.value

    @property
    def description(self):
        if self == ProjectCreationStatus.SUCCESS:
            return 'Successfully created new project'
        elif self == ProjectCreationStatus.BAD_REQUEST:
            return 'Project creation failed: bad request'
        elif self == ProjectCreationStatus.ENPROCESSABLE_ENTITY:
            return 'Project creation failed: invalid input'


class ProjectCreationInput(graphene.InputObjectType):
    title = Title(required=True)
    description = Description(required=False)


class ProjectCreationPayload(graphene.ObjectType):
    record = graphene.Field(ProjectType, required=True)
    record_id = graphene.Int(required=True)
    status = graphene.Field(ProjectCreationStatus, required=True)


class ProjectCreation(BaseMutationPayload, graphene.Mutation):
    '''Entity for creation new project'''

    class Arguments:
        input = ProjectCreationInput(required=True)

    project_creation_payload = graphene.Field(
        ProjectCreationPayload, required=True)

    @staticmethod
    @login_required
    async def mutate(parent, info: ResolveInfo, input: ProjectCreationInput):
        app = info.context['request'].app
        data = validate_input(input, ProjectCreationSchema)
        data['created_by'] = info.context['request']['user_id']
        await check_if_project_exists(app['db'], data)

        project = await create_project(app['db'], data)

        return ProjectCreation(
            project_creation_payload=ProjectCreationPayload(
                record=project,
                record_id=project['id'],
                status=ProjectCreationStatus.SUCCESS,
            )
        )
