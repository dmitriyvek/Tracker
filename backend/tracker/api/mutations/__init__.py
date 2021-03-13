import graphene

from .auth import AuthRootMutation
from .projects import ProjectRootMutation


class Mutation(graphene.ObjectType):
    auth = graphene.Field(AuthRootMutation, required=True)
    project = graphene.Field(ProjectRootMutation, required=True)

    def resolve_auth(parent, info):
        return {}

    def resolve_project(parent, info):
        return {}
