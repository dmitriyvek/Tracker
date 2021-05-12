import graphene

from tracker.api.types import UserDuplicationChecksType


class AuthDuplicationCheckQuery(graphene.ObjectType):
    duplication_check = graphene.Field(
        UserDuplicationChecksType,
        description='Check user\'s credentials duplication',
        required=True
    )

    def resolve_duplication_check(parent, info):
        return {}
