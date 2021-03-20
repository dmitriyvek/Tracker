import graphene
from graphql import ResolveInfo

from tracker.api.types import ProjectType, ProjectConnection
from tracker.api.wrappers import login_required
from tracker.api.services.projects import get_user_project_list, validate_connection_params


class ProjectListQuery(graphene.ObjectType):
    list = graphene.relay.ConnectionField(
        ProjectConnection,
        description='List of all projects in which the currently loged user participates',
        required=True
    )

    @login_required
    async def resolve_list(parent, info: ResolveInfo, **connection_params):
        db = info.context['request'].app['db']
        user_id = info.context['request'].get('user_id')

        connection_params = validate_connection_params(connection_params)
        records = await get_user_project_list(
            db, info, user_id, connection_params
        )

        return records
