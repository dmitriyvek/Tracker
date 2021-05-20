from dataclasses import dataclass

from asyncpgsa import PG

from tracker.api.services.auth import generate_password_hash
from tracker.db.schema import roles_table, users_table


@dataclass
class RegisterByRoleTokenData:
    assign_by: int
    email: str
    password: str
    project_id: int
    role: str
    username: str


async def create_user_and_role_by_role_token(
    db: PG, data: RegisterByRoleTokenData
) -> dict:
    '''
    Creates and returns new user with new role in given project
    '''
    data.password = generate_password_hash(data.password)

    async with db.transaction() as conn:
        query = users_table.\
            insert().\
            returning(
                users_table.c.id,
                users_table.c.username,
                users_table.c.email
            ).\
            values({
                'email': data.email,
                'is_confirmed': True,
                'password': data.password,
                'username': data.username,
            })
        user = dict(await conn.fetchrow(query))

        query = roles_table.\
            insert().\
            values({
                'user_id': user['id'],
                'role': data.role,
                'project_id': data.project_id,
                'assign_by': data.assign_by,
            })
        await conn.fetchrow(query)

    return user
