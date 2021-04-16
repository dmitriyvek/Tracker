import graphene
from graphql import ResolveInfo

from tracker.api.types import ProjectDuplicationChecksType


class ProjectDuplicationCheckQuery(graphene.ObjectType):
    duplication_check = graphene.Field(
        ProjectDuplicationChecksType,
        description='Check if user already have a project with given title',
        required=True
    )

    def resolve_duplication_check(parent, info):
        return {}
