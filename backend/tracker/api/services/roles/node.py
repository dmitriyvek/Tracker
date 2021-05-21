from typing import Dict, Union

from asyncpgsa import PG
from graphene.types import ResolveInfo
from sqlalchemy.sql import and_

from tracker.api.errors import APIException
from tracker.api.services.roles import ROLES_REQUIRED_FIELDS
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import roles_table


async def get_role_node(
    db: PG,
    info: ResolveInfo,
    role_id: int,
    user_id: int
) -> Union[Dict, None]:
    '''
    Get a role with given id.
    Raise 403 if user don't have this role.
    '''

    query = roles_table.\
        select().\
        with_only_columns(ROLES_REQUIRED_FIELDS).\
        where(and_(
            roles_table.c.id == role_id,
            roles_table.c.is_deleted.is_(False)
        ))
    record = dict(await db.fetchrow(query))

    if not record:
        return None

    if not record['user_id'] == user_id:
        raise APIException(
            'You are not allowed to see this.',
            status=StatusEnum.UNAUTHORIZED.name
        )

    return record
