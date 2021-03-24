from typing import Union, Dict

from asyncpg import Record
from asyncpgsa import PG
from graphene.types import ResolveInfo
from graphql.language.ast import InlineFragment
from sqlalchemy import and_

from .base import PROJECTS_REQUIRED_FIELDS, format_project_type
from tracker.api.errors import APIException
from tracker.api.services.roles import ROLES_REQUIRED_FIELDS
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import roles_table, projects_table


# TODO: may be universal
def check_role_requested_in_node(info: ResolveInfo) -> bool:
    '''Parses projectType node\'s field_asts and check if current user role is requested'''

    # TODO: assumed concrete field_asts structure, is it always the same?
    for field in info.field_asts[0].selection_set.selections:
        if isinstance(field, InlineFragment):
            if field.type_condition.name.value == 'ProjectType':

                for field in field.selection_set.selections:
                    if field.name.value == 'myRole':
                        return True

                return False


async def get_user_project_role(db: PG, project_id: int, user_id: int) -> Record:
    '''Get role with given user id and project id. If not raise 403'''
    query = roles_table.\
        select().\
        with_only_columns([
            *ROLES_REQUIRED_FIELDS,
        ]).\
        where(and_(
            roles_table.c.user_id == user_id,
            roles_table.c.project_id == project_id,
            roles_table.c.is_deleted.is_(False)
        ))
    record = await db.fetchrow(query)

    if not record:
        raise APIException(
            'You are not a member of this project.',
            status=StatusEnum.FORBIDDEN.name
        )

    return record


async def get_project_node(db: PG, info: ResolveInfo, project_id: int, user_id: int) -> Union[Dict, None]:
    '''Get a project with given id. Raise 403 if user is not member of this project'''
    query = projects_table.\
        select().\
        with_only_columns([
            *PROJECTS_REQUIRED_FIELDS,
        ]).\
        where(and_(
            projects_table.c.id == project_id,
            projects_table.c.is_deleted.is_(False)
        ))
    project = await db.fetchrow(query)

    if not project:
        return None

    if not check_role_requested_in_node(info):
        return dict(project)

    role = await get_user_project_role(db, project_id, user_id)
    result = format_project_type({**project, **role})

    return result
