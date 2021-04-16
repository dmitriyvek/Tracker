from asyncpgsa import PG
from sqlalchemy import and_, exists, select, literal_column

from .base import PROJECTS_REQUIRED_FIELDS
from tracker.api.errors import APIException
from tracker.api.services.roles import ROLES_REQUIRED_FIELDS
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import UserRoleEnum, projects_table, roles_table


async def check_if_project_exists(db: PG, data: dict) -> None:
    '''
    Checks if project with given title is already created by given user 
    if yes raises 400 error
    '''
    query = projects_table.\
        select().\
        with_only_columns([literal_column('1')]).\
        where(and_(
            projects_table.c.title == data['title'],
            projects_table.c.created_by == data['created_by'],
            projects_table.c.is_deleted.is_(False)
        ))
    query = select([exists(query)])

    result = await db.fetchval(query)
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
                'role': UserRoleEnum.project_manager,
                'user_id': data['created_by'],
                'project_id': project['id'],
                'assign_by': data['created_by'],
            })
        role = dict(await conn.fetchrow(role_query))

    project['my_role'] = role
    return project
