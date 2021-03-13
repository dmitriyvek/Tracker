import graphene

from .list import ProjectListQuery


class ProjectsQuery(graphene.ObjectType):
    list = graphene.Field(ProjectListQuery)

    def resolve_list(parent, info):
        return {}
