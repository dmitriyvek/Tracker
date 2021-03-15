import graphene


class RoleType(graphene.ObjectType):
    role = graphene.String(
        required=True,
        description='A name of given role',
    )
    user_id = graphene.Int(
        required=True,
        description='The id of user which has this role',
    )
    project_id = graphene.Int(
        required=True,
        description='The id of the project to which this role is associated',
    )
    assign_by = graphene.Int(
        required=True,
        description='The id of user which created this role',
    )
    assign_at = graphene.DateTime(
        required=True,
        description='Role creation timestamp',
    )
