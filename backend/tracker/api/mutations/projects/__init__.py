import graphene

from .create import ProjectCreation


class ProjectRootMutation(graphene.ObjectType):
    project_creation = ProjectCreation.Field()
