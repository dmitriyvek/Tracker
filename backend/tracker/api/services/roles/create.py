from dataclasses import dataclass
from datetime import datetime

from asyncpg.exceptions import ForeignKeyViolationError
from asyncpgsa import PG
from sqlalchemy import and_, exists, select

from .base import ROLES_REQUIRED_FIELDS
from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import UserRoleEnum, roles_table


@dataclass
class RoleData:
    role: UserRoleEnum
    user_id: int
    project_id: int
    assign_by: int


@dataclass
class RoleResponseData(RoleData):
    id: int
    assign_at: datetime


async def check_if_user_is_project_manager(
    db: PG, user_id: int, project_id: int
):
    '''
    Checks if user has project manager role in given project
    if not raise 403
    '''
    query = roles_table.\
        select().\
        with_only_columns([roles_table.c.id]).\
        where(and_(
            roles_table.c.role == UserRoleEnum.__members__[
                'project_manager'].value,
            roles_table.c.user_id == user_id,
            roles_table.c.project_id == project_id,
            roles_table.c.is_deleted.is_(False)
        ))
    query = select([exists(query)])

    result = await db.fetchval(query)
    if not result:
        raise APIException(
            'You must be a project manager to add new users in a project.',
            status=StatusEnum.FORBIDDEN.name
        )


async def check_user_role_duplication(
    db: PG, user_id: int, project_id: int
) -> bool:
    '''
    Checks if user already has a role in given project
    return True if it does 
    '''
    query = roles_table.\
        select().\
        with_only_columns([roles_table.c.id]).\
        where(and_(
            roles_table.c.user_id == user_id,
            roles_table.c.project_id == project_id,
            roles_table.c.is_deleted.is_(False)
        ))
    query = select([exists(query)])

    result = await db.fetchval(query)
    return result


async def check_if_role_exists(db: PG, data: RoleData) -> None:
    '''
    Checks if user already has a role in given project
    if yes raises 400 error
    '''
    query = roles_table.\
        select().\
        with_only_columns([roles_table.c.id]).\
        where(and_(
            roles_table.c.user_id == data['user_id'],
            roles_table.c.project_id == data['project_id'],
            roles_table.c.is_deleted.is_(False),
        ))
    query = select([exists(query)])

    result = await db.fetchval(query)
    if result:
        raise APIException(
            'User already has a role in given project.',
            status=StatusEnum.BAD_REQUEST.name
        )


async def create_role(db: PG, data: RoleData) -> RoleResponseData:
    '''Creates and returns new role'''

    query = roles_table.insert().\
        returning(roles_table.c.id, *ROLES_REQUIRED_FIELDS).\
        values(data)

    try:
        role = dict(await db.fetchrow(query))
    except ForeignKeyViolationError:
        raise APIException(
            'Invalid project id or user id.',
            status=StatusEnum.BAD_REQUEST.name
        )

    return role
