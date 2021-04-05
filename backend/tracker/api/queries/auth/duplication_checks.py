import graphene
from graphql import ResolveInfo

from tracker.api.types import DuplicationChecksType


class DuplicationCheckQuery(graphene.ObjectType):
    duplication_check = graphene.Field(
        DuplicationChecksType,
        description='Check user\'s credentials duplication',
        required=True
    )

    def resolve_duplication_check(parent, info):
        return {}
