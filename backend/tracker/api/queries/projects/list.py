import graphene
from graphql import ResolveInfo

from tracker.api.connections import validate_connection_params, create_connection_from_records_list
from tracker.api.connections.projects import ProjectConnection
from tracker.api.types import ProjectType
from tracker.api.wrappers import login_required
from tracker.api.services.projects import get_user_project_list


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

        connection_params = validate_connection_params(
            connection_params,
            ProjectType
        )
        record_list = await get_user_project_list(
            db, info, user_id, connection_params
        )

        return create_connection_from_records_list(
            record_list,
            connection_params,
            ProjectConnection,
            ProjectType
        )
