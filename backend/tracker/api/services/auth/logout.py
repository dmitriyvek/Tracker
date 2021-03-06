from asyncpgsa import PG

from tracker.db.schema import blacklist_tokens_table


async def create_blacklist_token(db: PG, token: str) -> None:
    '''Creates blacklist token'''
    await db.fetchval(
        blacklist_tokens_table.
        insert().
        values({'token': token})
    )
