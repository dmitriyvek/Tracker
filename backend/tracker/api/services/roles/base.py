from tracker.db.schema import roles_table


ROLES_REQUIRED_FIELDS = [
    roles_table.c.role,
    roles_table.c.user_id,
    roles_table.c.project_id,
    roles_table.c.assign_by,
    roles_table.c.assign_at,
]
