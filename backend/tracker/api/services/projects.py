from typing import List, Dict

from asyncpgsa import PG

from tracker.db.schema import projects_table
from tracker.api.status_codes import StatusEnum
from tracker.api.errors import APIException


async def get_user_projects(db: PG, user_id: int) -> List[Dict]:
    '''Get a list of all projects in which the user participates '''
    query = projects_table.select().\
        with_only_columns([
            projects_table.c.id,
            projects_table.c.title,
            projects_table.c.description,
            projects_table.c.created_at
        ])
    result = await db.query(query)
    result = list(map(lambda record: {**record}, result))
    return result


async def check_if_project_exists(db: PG, data: dict) -> None:
    '''Checks if project with given title is already exist if yes raises 400 error'''
    query = projects_table.select().\
        with_only_columns([projects_table.c.id]).\
        where(projects_table.c.title == data['title'])

    result = await db.fetchrow(query)
    if result:
        raise APIException(
            'Project with given title is already exist.', status=StatusEnum.BAD_REQUEST.name)


async def create_project(db: PG, data: dict) -> dict:
    '''Creates and returns new project'''
    query = projects_table.insert().\
        returning(
            projects_table.c.id,
            projects_table.c.title,
            projects_table.c.description
    ).\
        values(data)
    project = dict(await db.fetchrow(query))

    return project
