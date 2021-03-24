import graphene
from graphql import ResolveInfo

from tracker.api.types.project import ProjectType
from tracker.api.services.projects import get_total_count_of_user_projects


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
