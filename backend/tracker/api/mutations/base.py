import graphene


class BaseMutationPayload(graphene.ObjectType):
    query = graphene.Field('tracker.api.queries.Query', required=True)

    def resolve_query(parent, info):
        return {}
