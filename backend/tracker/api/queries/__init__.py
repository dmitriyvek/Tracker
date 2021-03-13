import graphene
from graphene.relay import Node

from .users import UsersQuery
from .projects import ProjectsQuery


class Query(graphene.ObjectType):
    '''
    The main GraphQL query point.
    '''
    users = graphene.Field(UsersQuery)
    projects = graphene.Field(ProjectsQuery)
    node = Node.Field()

    def resolve_users(self, info):
        return {}

    def resolve_projects(self, info):
        return {}
