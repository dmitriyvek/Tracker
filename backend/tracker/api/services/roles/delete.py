from asyncpgsa import PG
from sqlalchemy.sql import and_

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import (
    UserRoleEnum, projects_table, roles_table
)


async def check_user_priviliges_for_role_deletion(
    db: PG, role_id: int, deletion_by_id: int,
):
    '''
    Checks if user has enough privileges for deletion given role
    in this project if not raise 403.
    '''
    # geting role for deletion
    get_role_query = roles_table.\
        select().\
        with_only_columns([
            roles_table.c.role,
            roles_table.c.user_id,
            roles_table.c.project_id,
        ]).\
        where(and_(
            roles_table.c.id == role_id,
            roles_table.c.is_deleted.is_(False),
        ))

    role_to_delete = await db.fetchrow(get_role_query)

    if not role_to_delete:
        raise APIException(
            'Invalid role id.',
            status=StatusEnum.BAD_REQUEST.name
        )

    # geting role of user which requests a deletion
    # (another request because we do not know a project id)
    deletion_by_role_query = roles_table.\
        select().\
        with_only_columns([roles_table.c.role]).\
        where(and_(
            roles_table.c.user_id == deletion_by_id,
            roles_table.c.project_id == role_to_delete['project_id'],
            roles_table.c.is_deleted.is_(False)
        ))

    deletion_by_role = await db.fetchrow(deletion_by_role_query)

    if not deletion_by_role or \
            deletion_by_role['role'] != UserRoleEnum.project_manager.value:
        raise APIException(
            'You do not have enough priviliges for this operation.',
            status=StatusEnum.FORBIDDEN.name
        )

    # assuming that project's creator has project manager role in his project
    if role_to_delete['role'] == UserRoleEnum.project_manager.value:
        # check if user which requests a deletion is project's creator
        get_project_creator_query = projects_table.\
            select().\
            with_only_columns([projects_table.c.created_by]).\
            where(and_(
                projects_table.c.id == role_to_delete['project_id'],
                projects_table.c.is_deleted.is_(False)
            ))

        project_creator_id = await db.fetchval(get_project_creator_query)

        if deletion_by_id != project_creator_id:
            raise APIException(
                'You must have a project\'s creator '
                'role to delete project manager role.',
                status=StatusEnum.FORBIDDEN.name
            )

        # if project's creator role deletion is requested
        if role_to_delete['user_id'] == project_creator_id:
            raise APIException(
                'You can not delete project\'s creator role.',
                status=StatusEnum.FORBIDDEN.name
            )


async def delete_role_by_id(
    db: PG, role_id: int
):
    '''
    Mark role with given id as deleted.
    '''
    query = roles_table.\
        update().\
        values(is_deleted=True).\
        where(roles_table.c.id == role_id)

    await db.fetchrow(query)
