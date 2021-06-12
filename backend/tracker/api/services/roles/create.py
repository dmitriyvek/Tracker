from dataclasses import dataclass
from typing import List

from asyncpgsa import PG
from sqlalchemy import and_

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import (
    UserRoleEnum, projects_table, roles_table, users_table
)


@dataclass
class RolesData:
    role: UserRoleEnum
    email_list: List[str]
    project_id: int
    assign_by: int
    title: str


async def check_if_user_is_project_manager(
    db: PG, user_id: int, project_id: int
):
    '''
    Checks if user has project manager role in given project
    if not raise 403, if yes returns project title.
    (title is for email)
    '''
    query = roles_table.\
        join(
            projects_table,
            roles_table.c.project_id == projects_table.c.id
        ).\
        select().\
        with_only_columns([projects_table.c.title]).\
        where(and_(
            roles_table.c.role == UserRoleEnum.__members__[
                'project_manager'].value,
            roles_table.c.user_id == user_id,
            roles_table.c.project_id == project_id,
            roles_table.c.is_deleted.is_(False)
        ))

    title = await db.fetchval(query)
    if not title:
        raise APIException(
            'You must be a project manager for this operation.',
            status=StatusEnum.FORBIDDEN.name
        )

    return title


async def get_emails_of_duplicated_roles(db: PG, data: RolesData) -> List[str]:
    '''
    Checks if users with given emails already have a role in given project.
    Returns email list of such users.
    '''
    email_list = data.email_list

    query = roles_table.\
        join(
            users_table,
            roles_table.c.user_id == users_table.c.id
        ).\
        select().\
        with_only_columns([
            users_table.c.email,
        ]).\
        where(and_(
            roles_table.c.project_id == data.project_id,
            users_table.c.email.in_(email_list),
            roles_table.c.is_deleted.is_(False),
            users_table.c.is_deleted.is_(False)
        ))

    result = await db.fetch(query)
    result = list(map(lambda record: record['email'], result))
    return result


def get_rid_of_duplications(
    data: RolesData,
    duplicated_email_list: List[str]
) -> RolesData:
    '''
    Get rid of duplicated emails in data.email_list
    '''
    email_list = data.email_list

    for email in duplicated_email_list:
        for i in range(len(email_list)):
            if email_list[i] == email:
                del email_list[i]
                break

    return data
