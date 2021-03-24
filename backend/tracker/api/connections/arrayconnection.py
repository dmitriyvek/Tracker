from base64 import b64encode, b64decode
from typing import Dict, Union, List, Any

import graphene
from asyncpg import Record
from graphene.relay import Connection, PageInfo
from graphql_relay import from_global_id, to_global_id
from sqlalchemy.schema import Table

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum


# TODO: use it in doc explorer
class CustomPageInfo(PageInfo):

    class Meta:
        description = (
            "The Relay compliant `PageInfo` type, containing data necessary to"
            " paginate this connection. Max fetch number = 20"
        )


def validate_connection_params(
    params: Dict[str, str],
    node_type: graphene.ObjectType,
    max_fetch_number: int = 20,
) -> Dict[str, Union[str, int]]:
    '''
    Validate connection params. Returns dict with
    decoded (as integer) "after" and "before" cursors if given.
    Set "first" to max_fetch_number if not given or greater
    '''

    if params:

        for key in ('first', 'last'):
            param = params.get(key)

            if param and param > max_fetch_number:
                params[key] = max_fetch_number

            if param and param < 0:
                raise APIException(
                    f'value of "{key}" parameter must be greater then 0',
                    status=StatusEnum.BAD_REQUEST.name
                )

        for key in ('after', 'before'):
            if param := params.get(key):
                try:
                    param = from_global_id(param)
                    if param[0] != node_type.__name__ or int(param[1]) < 0:
                        raise Exception

                    # cursor is now id
                    params[key] = int(param[1])
                except:
                    raise APIException(
                        f'value of "{key}" is not a valid cursor',
                        status=StatusEnum.BAD_REQUEST.name
                    )

    if not params.get('first') and not params.get('last'):
        params['first'] = max_fetch_number

    return params


def base64(s: str) -> str:
    return b64encode(s.encode('utf-8')).decode('utf-8')


def unbase64(s: str) -> str:
    return b64decode(s).decode('utf-8')


def id_to_cursor(node_type: graphene.ObjectType, id: int):
    '''Creates the cursor string from a node type and record id'''
    return base64(f'{node_type.__name__}:{str(id)}')


def cursor_to_id(cursor):
    '''Rederives the id from the cursor string.'''
    try:
        return int(unbase64(cursor).split(':', 1)[1])
    except Exception:
        return None


def modify_query_by_connection_params(
    query,
    table: Table,
    params: Dict[str, Union[str, int]]
):
    '''Modify the database query according to the connection parameters'''

    if after := params.get('after'):
        query = query.where(table.c.id > after)

    if before := params.get('before'):
        query = query.where(table.c.id < before)

    last = params.get('last')

    if first := params.get('first'):
        if not last or first == last:
            query = query.order_by(table.c.id.asc()).limit(first + 1)

        else:
            query = query.order_by(table.c.id.asc()).limit(first)
            sub_query = query.alias('sub_query')
            query = sub_query.\
                select().\
                order_by(sub_query.c.id.desc()).\
                limit(last + 1)

    elif last:
        query = query.order_by(table.c.id.desc()).limit(last + 1)

    return query


def create_connection_from_records_list(
    record_list: List[Union[Dict[str, Any], Record]],
    connection_params: Dict[str, str],
    connection_type: Connection,
    node_type: graphene.ObjectType,
    pageinfo_type: PageInfo = PageInfo,
) -> Connection:

    edge_type = connection_type.Edge

    after = connection_params.get('after')
    before = connection_params.get('before')
    first = connection_params.get('first')
    last = connection_params.get('last')

    has_previous_page = False
    has_next_page = False
    result_length = len(record_list)

    if last and first != last:
        record_list.reverse()

    if result_length:

        if after:
            has_previous_page = True

        # assuming that id in cursor is valid
        # (not made too large by some client)
        if before:
            has_next_page = True

        if first and not last or first == last != None:
            if result_length == first + 1:
                has_next_page = True
                record_list.pop()

        elif last and result_length == last + 1:
            has_previous_page = True
            record_list.pop(0)

    edge_list = [
        edge_type(
            node=node,
            cursor=id_to_cursor(node_type, node['id'])
        )
        for node in record_list
    ]

    first_edge_cursor = edge_list[0].cursor if edge_list else None
    last_edge_cursor = edge_list[-1].cursor if edge_list else None

    return connection_type(
        edges=edge_list,
        page_info=pageinfo_type(
            start_cursor=first_edge_cursor,
            end_cursor=last_edge_cursor,
            has_previous_page=has_previous_page,
            has_next_page=has_next_page
        )
    )
