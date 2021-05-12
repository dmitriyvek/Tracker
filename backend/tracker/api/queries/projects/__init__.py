from .list import ProjectListQuery
from .duplication_checks import ProjectDuplicationCheckQuery


class ProjectsQuery(
    ProjectDuplicationCheckQuery,
    ProjectListQuery,
):
    pass
