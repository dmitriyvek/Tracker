from collections import defaultdict
from typing import Dict

from aiodataloader import DataLoader
from asyncpgsa import PG
from sqlalchemy import Table

from tracker.api.connections import modify_query_by_connection_params
from tracker.db.schema import roles_table


def get_generic_loader(
    db: PG,
    table: Table,
    attr: str,
    connection_params: Dict[str, str],
) -> DataLoader:

    class GenericLoader(DataLoader):

        async def batch_load_fn(self, key_list: list):
            records_by_attr = defaultdict(list)

            lookup = getattr(table.c, attr).in_(key_list)
            query = table.select().where(lookup)

            query = modify_query_by_connection_params(
                query,
                roles_table,
                connection_params
            )

            record_list = await db.fetch(query)

            for record in record_list:
                records_by_attr[record[attr]].append(dict(record))

            result = [records_by_attr.get(key, []) for key in key_list]
            return result

    return GenericLoader
