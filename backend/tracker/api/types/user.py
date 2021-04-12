import graphene
from graphene.types import ResolveInfo
from sqlalchemy import and_

from tracker.api.scalars.auth import Email, Username
from tracker.api.connections import (
    CustomPageInfo, create_connection_from_record_list,
    validate_connection_params
)
from tracker.api.services.users import get_user_by_id
from tracker.api.services.projects import get_user_project_list
from tracker.api.types.project import ProjectType, ProjectConnection
from tracker.api.wrappers import login_required
from tracker.db.schema import users_table


class UserType(graphene.ObjectType):
    '''
    A user is an individual's account on current api
    that can take part in projects.
    '''

    username = Username(
        required=True,
        description='A username of user',
    )
    email = Email(
        required=True,
        description='A email of user',
    )
    registered_at = graphene.DateTime(
        required=True,
        description='User registration timestamp',
    )
    project_list = graphene.relay.ConnectionField(
        ProjectConnection,
        required=True,
        description='List of projects in which user participates',
    )

    class Meta:
        interfaces = (graphene.relay.Node, )

    @staticmethod
    async def resolve_project_list(
        parent,
        info: ResolveInfo,
        **connection_params
    ):
        user_id = info.context['request']['user_id']
        db = info.context['request'].app['db']
        max_fetch_number = info.context['request'].app.\
            get('config', {}).\
            get('max_fetch_number')

        connection_params = validate_connection_params(
            connection_params,
            ProjectType,
            max_fetch_number
        )
        record_list = await get_user_project_list(
            db, info, user_id, connection_params
        )

        return create_connection_from_record_list(
            record_list,
            connection_params,
            ProjectConnection,
            ProjectType,
            CustomPageInfo
        )

    @classmethod
    @login_required
    async def get_node(cls, info, user_id):
        user_id = int(user_id)
        db = info.context['request'].app['db']

        record = await get_user_by_id(db, user_id)
        record = cls(**record)

        return record
