import graphene

from .list import ProjectListQuery
from .duplication_checks import DuplicationCheckQuery


class ProjectsQuery(
    DuplicationCheckQuery,
    ProjectListQuery, 
):
    pass
