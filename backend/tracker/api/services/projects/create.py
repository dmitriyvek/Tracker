from asyncpgsa import PG

from .base import PROJECTS_REQUIRED_FIELDS
from tracker.api.errors import APIException
from tracker.api.services.roles import ROLES_REQUIRED_FIELDS
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import UserRole, projects_table, roles_table


async def check_if_project_exists(db: PG, data: dict) -> None:
    '''Checks if project with given title is already exist if yes raises 400 error'''
    query = projects_table.\
        select().\
        with_only_columns([projects_table.c.id]).\
        where(projects_table.c.title == data['title'])

    result = await db.fetchrow(query)
    if result:
        raise APIException(
            'Project with given title is already exist.',
            status=StatusEnum.BAD_REQUEST.name
        )


async def create_project(db: PG, data: dict) -> dict:
    '''Creates and returns new project and role'''

    async with db.transaction() as conn:
        project_query = projects_table.insert().\
            returning(*PROJECTS_REQUIRED_FIELDS).\
            values(data)
        project = dict(await conn.fetchrow(project_query))

        role_query = roles_table.insert().\
            returning(*ROLES_REQUIRED_FIELDS).\
            values({
                'role': UserRole.project_manager,
                'user_id': data['created_by'],
                'project_id': project['id'],
                'assign_by': data['created_by'],
            })
        role = dict(await conn.fetchrow(role_query))

    project['my_role'] = role
    return project


# query = union(projects_table.select().with_only_columns([literal_column('1').label('num'), projects_table.c.id]).where(projects_table.c.id == 2), roles_table.select(
# ).with_only_columns([literal_column('2').label('num'), roles_table.c.user_id]).where(roles_table.c.project_id == 2)).order_by('num')
