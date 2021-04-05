import graphene
from graphene.relay import Node

from .auth import AuthQuery
from .projects import ProjectsQuery
from .users import UsersQuery


class Query(graphene.ObjectType):
    '''
    The main GraphQL query point.
    '''
    auth = graphene.Field(AuthQuery)
    projects = graphene.Field(ProjectsQuery)
    users = graphene.Field(UsersQuery)
    node = Node.Field()

    def resolve_users(self, info):
        return {}

    def resolve_projects(self, info):
        return {}

    def resolve_auth(self, info):
        return {}
