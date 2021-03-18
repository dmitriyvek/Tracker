from typing import Union, Dict

from asyncpg import Record

from tracker.db.schema import projects_table


# fields of tracker.api.types.projects.ProjectType
PROJECTS_REQUIRED_FIELDS = [
    projects_table.c.id,
    projects_table.c.title,
    projects_table.c.description,
    projects_table.c.created_at,
]


def format_project_type(record: Union[Record, Dict]) -> dict:
    '''Format project record'''
    return {
        'id': record['id'],
        'title': record['title'],
        'description': record['description'],
        'created_at': record['created_at'],
        'my_role': {
            'user_id': record['user_id'],
            'role': record['role'],
            'project_id': record['project_id'],
            'assign_by': record['assign_by'],
            'assign_at': record['assign_at'],
        }
    }
