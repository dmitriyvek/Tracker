from functools import partial

import graphene
import asyncio
from graphql_server import default_format_error
from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

from tracker.api.queries import Query
from tracker.api.mutations import Mutation
from tracker.api.middleware import GraphQLErrorMiddleware


def format_error(error):
    '''Custom error formater that adds all arguments from exception.context'''
    formatted_error = default_format_error(error)

    try:
        formatted_error.update(error.original_error.context)
    except AttributeError:
        pass

    return formatted_error


schema = graphene.Schema(
    query=Query,
    mutation=Mutation
)


GraphQLView = partial(
    GraphQLView,
    schema=schema,
    executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
    enable_async=True,
    error_formatter=format_error,
    middleware=[GraphQLErrorMiddleware(), ]
)


gqil_view = GraphQLView(
    graphiql=True,
)

gql_view = GraphQLView(
    graphiql=False,
)
