import argparse

import sqlalchemy as sa
from yarl import URL

from tracker.utils.db import get_db_url
from tracker.api.services import generate_password_hash
from tracker.db.schema import (
    users_table, projects_table, roles_table, tickets_table, comments_table,
    UserRole as URole, TicketStatus as TS,
    TicketPriority as TP, TicketType as TT
)


USER_PSWD = generate_password_hash('zxcfghuio')


def init_db_data():
    '''
    Initialized db with test data (working with empty tables only)
    '''
    user_list = [{
        'username': f'user{i}',
        'password': USER_PSWD,
        'email': f'user{i}@mail.com',
        'is_admin': False
    } for i in range(1, 11)]
    user_list[0]['username'] = 'admin'
    user_list[0]['is_admin'] = True

    project_list = [{
        'title': f'project{i}',
        'description': f'description{i}',
        'created_by': user_id
    } for i, user_id in (
        (1, 1),
        (2, 1),
        (3, 2)
    )]

    role_list = [{
        'project_id': project_id,
        'user_id': user_id,
        'assign_by': by_id,
        'role': role
    } for project_id, user_id, by_id, role in (
        (1, 1, 1, URole.project_manager),
        (1, 2, 1, URole.project_manager),
        (1, 3, 2, URole.team_member),
        (1, 4, 1, URole.team_member),
        (1, 5, 2, URole.team_member),
        (1, 6, 1, URole.viewer),
        (2, 1, 1, URole.project_manager),
        (2, 5, 1, URole.team_member),
        (2, 6, 1, URole.team_member),
        (2, 7, 1, URole.viewer),
        (3, 2, 2, URole.project_manager),
        (3, 1, 2, URole.team_member),
        (3, 3, 2, URole.team_member)
    )]

    ticket_list = [{
        'project_id': project_id,
        'created_by': by_id,
        'assigned_to': to_id,
        'title': f'title{i}',
        'description': f'description{i}',
        'status': status,
        'priority': priority,
        'type': type
    } for i, project_id, by_id, to_id, status, priority, type in (
        (1, 1, 1, 4, TS.open, TP.hight, TT.feature_request),
        (2, 1, 1, 3, TS.in_progress, TP.medium, TT.feature_request),
        (3, 1, 1, 5, TS.done, TP.hight, TT.bug_or_error),
        (4, 1, 1, 6, TS.open, TP.none, TT.document_request),
        (5, 1, 2, 4, TS.done, TP.medium, TT.bug_or_error),
        (6, 1, 2, 3, TS.in_progress, TP.hight, TT.feature_request),
        (7, 1, 2, 5, TS.open, TP.none, TT.feature_request),
        (8, 2, 2, 1, TS.open, TP.medium, TT.feature_request),
        (9, 2, 2, 1, TS.done, TP.hight, TT.bug_or_error),
        (10, 2, 2, 3, TS.in_progress, TP.none, TT.feature_request),
        (11, 2, 2, 1, TS.in_progress, TP.medium, TT.document_request),
        (12, 2, 2, 1, TS.open, TP.hight, TT.feature_request),
        (13, 3, 3, 1, TS.open, TP.hight, TT.feature_request),
        (14, 3, 3, 1, TS.done, TP.none, TT.document_request),
        (15, 3, 3, 2, TS.open, TP.medium, TT.feature_request)
    )]

    comment_list = [{
        'content': 'contect{i}',
        'ticket_id': ticket_id,
        'user_id': user_id
    } for i, ticket_id, user_id in (
        (1, 1, 1),
        (2, 1, 2),
        (3, 1, 1),
        (4, 2, 3),
        (5, 3, 1),
        (6, 3, 5),
        (7, 4, 1)
    )]

    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--db-url', type=URL, default=get_db_url(),
        help='Database URL'
    )

    result = parser.parse_args()
    db_url = str(result.db_url)
    engine = sa.create_engine(db_url)

    # check if tables are empty
    with engine.connect() as conn:
        query = sa.select([
            users_table.c.id,
            projects_table.c.id,
            tickets_table.c.id,
            roles_table.c.id,
            comments_table.c.id,
        ]).limit(1)
        if conn.execute(query).rowcount:
            print('Tables not empty - can not initialize test data')
            return

    # init transaction connection
    with engine.begin() as conn:
        conn.execute(users_table.insert(), user_list)
        conn.execute(projects_table.insert(), project_list)
        conn.execute(roles_table.insert(), role_list)
        conn.execute(tickets_table.insert(), ticket_list)
        conn.execute(comments_table.insert(), comment_list)

    print('Successfully initialized db with test data')


if __name__ == '__main__':
    init_db_data()
