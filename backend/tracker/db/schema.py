from enum import Enum, unique

import sqlalchemy as sa


convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = sa.MetaData(naming_convention=convention)


@unique
class UserRoleEnum(Enum):
    '''
    Variants of roles that users can have in a project.
    One project - one role.
    '''
    project_manager = 'project_manager'
    team_member = 'team_member'
    viewer = 'viewer'


@unique
class TicketStatusEnum(Enum):
    '''Variants of ticket complition status'''
    open = 'open'
    in_progress = 'in_progress'
    done = 'done'


@unique
class TicketPriorityEnum(Enum):
    '''Variants of ticket complition priority'''
    none = 'none'
    low = 'low'
    medium = 'medium'
    hight = 'hight'


@unique
class TicketTypeEnum(Enum):
    '''Variants of ticket type'''
    bug_or_error = 'bug_or_error'
    feature_request = 'feature_request'
    document_request = 'document_request'
    other = 'other'


users_table = sa.Table(
    'users',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String, unique=True, nullable=False, index=True),
    sa.Column('password', sa.String, nullable=False),
    sa.Column('email', sa.String, unique=True, nullable=False),
    sa.Column('registered_at', sa.DateTime, default=sa.func.current_timestamp(
    ), nullable=False),
    sa.Column('is_admin', sa.Boolean, nullable=False, default=False,
              comment='If user has admin priviliges in app'),
    sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
    comment='Representation of user'
)

projects_table = sa.Table(
    'projects',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('title', sa.String, nullable=False),
    sa.Column('description', sa.String, nullable=True),
    sa.Column('created_at', sa.DateTime, default=sa.func.current_timestamp(
    ), nullable=False),
    sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),

    sa.Column('created_by', sa.Integer, sa.ForeignKey(
        'users.id', ondelete='CASCADE'
    ), nullable=False),

    sa.Index('ix__projects__created_by__title',
             'created_by', 'title', unique=True),

    comment='Representation of project (collection of tickets and user roles)'
)

roles_table = sa.Table(
    'roles',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('role', sa.Enum(UserRoleEnum, name='role'), nullable=False),
    sa.Column('assign_at', sa.DateTime,
              default=sa.func.current_timestamp(), nullable=False),
    sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),

    sa.Column('user_id', sa.Integer, sa.ForeignKey(
        'users.id', ondelete='CASCADE'
    ), nullable=False),

    sa.Column('project_id', sa.Integer, sa.ForeignKey(
        'projects.id', ondelete='CASCADE'
    ), nullable=False),

    sa.Column('assign_by', sa.Integer, sa.ForeignKey(
        'users.id', ondelete='CASCADE'
    ), nullable=False),

    sa.UniqueConstraint('user_id', 'project_id'),

    comment='Description of what role the user has in which project'
)

tickets_table = sa.Table(
    'tickets',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('title', sa.String, unique=True, nullable=False),
    sa.Column('description', sa.String, nullable=True),
    sa.Column('created_at', sa.DateTime, default=sa.func.current_timestamp(
    ), nullable=False),
    sa.Column('updated_at', sa.DateTime,
              onupdate=sa.func.current_timestamp(), nullable=True),
    sa.Column('status', sa.Enum(TicketStatusEnum, name='status'),
              nullable=False, default=TicketStatusEnum.open),
    sa.Column('priority', sa.Enum(TicketPriorityEnum, name='priority'),
              nullable=False, default=TicketPriorityEnum.none),
    sa.Column('type', sa.Enum(TicketTypeEnum, name='type'), nullable=False),
    sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),

    sa.Column('created_by', sa.Integer, sa.ForeignKey(
        'users.id', ondelete='CASCADE'
    ), nullable=False),

    sa.Column('assigned_to', sa.Integer, sa.ForeignKey(
        'users.id', ondelete='CASCADE'
    ), nullable=False),

    sa.Column('project_id', sa.Integer, sa.ForeignKey(
        'projects.id', ondelete='CASCADE'
    ), nullable=False),
)

comments_table = sa.Table(
    'comments',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('content', sa.String, nullable=False),
    sa.Column('created_at', sa.DateTime, default=sa.func.current_timestamp(
    ), nullable=False),
    sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),

    sa.Column('ticket_id', sa.Integer, sa.ForeignKey(
        'tickets.id', ondelete='CASCADE'
    ), nullable=False),

    sa.Column('user_id', sa.Integer, sa.ForeignKey(
        'users.id', ondelete='CASCADE'
    ), nullable=False, comment='Id of comment\'s author'),

    comment='Users comments on tickets'
)

blacklist_tokens_table = sa.Table(
    'blacklist_tokens',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('token', sa.String, unique=True, index=True, nullable=False),
    sa.Column('blacklisted_at', sa.DateTime, default=sa.func.current_timestamp(
    ), nullable=False),

    comment='Storage for blacklisted jwt auth tokens'
)
