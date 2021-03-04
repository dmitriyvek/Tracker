import graphene

from tracker.api.queries import Query


class BaseMutationPayload(graphene.ObjectType):
    # query = graphene.Field('tracker.api.queries.Query', required=True)
    query = graphene.Field(Query, required=True)

    def resolve_query(parent, info):
        return {}
