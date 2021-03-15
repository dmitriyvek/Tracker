import graphene
from graphql import ResolveInfo

from tracker.api.types import ProjectType
from tracker.api.wrappers import login_required
from tracker.api.services.projects import get_user_project_list


class ProjectListQuery(graphene.ObjectType):
    records = graphene.List(
        ProjectType,
        description='List of all projects in which the currently loged user participates',
        required=True
    )

    @login_required
    async def resolve_records(parent, info: ResolveInfo):
        db = info.context['request'].app['db']
        user_id = info.context['request'].get('user_id')

        records = await get_user_project_list(db, info, user_id)
        return records
