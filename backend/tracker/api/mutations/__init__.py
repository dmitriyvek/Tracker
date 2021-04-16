import graphene

from .auth import AuthRootMutation
from .projects import ProjectRootMutation
from .roles import RoleRootMutation


class Mutation(graphene.ObjectType):
    auth = graphene.Field(AuthRootMutation, required=True)
    project = graphene.Field(ProjectRootMutation, required=True)
    role = graphene.Field(RoleRootMutation, required=True)

    def resolve_auth(parent, info):
        return {}

    def resolve_project(parent, info):
        return {}

    def resolve_role(parent, info):
        return {}
