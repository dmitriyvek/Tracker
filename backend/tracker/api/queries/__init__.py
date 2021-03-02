import graphene
from graphene.relay import Node

from .auth import AuthQuery


class Query(graphene.ObjectType):
    '''
    The main GraphQL query point.
    '''
    auth = graphene.Field(AuthQuery)
    node = Node.Field()

    def resolve_auth(self, info):
        return {}
