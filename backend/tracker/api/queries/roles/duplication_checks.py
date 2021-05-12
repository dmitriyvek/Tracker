import graphene

from tracker.api.types import RoleDuplicationChecksType


class RoleDuplicationCheckQuery(graphene.ObjectType):
    duplication_check = graphene.Field(
        RoleDuplicationChecksType,
        description='Check if user already takes part in given project',
        required=True
    )

    def resolve_duplication_check(parent, info):
        return {}
