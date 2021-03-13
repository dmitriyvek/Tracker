import graphene
from graphene.relay import Node

from .users import UsersQuery


class Query(graphene.ObjectType):
    '''
    The main GraphQL query point.
    '''
    users = graphene.Field(UsersQuery)
    node = Node.Field()

    def resolve_users(self, info):
        return {}
