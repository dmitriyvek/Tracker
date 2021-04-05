import graphene


class Username(graphene.String):
    '''GraphQL string type with min length = 4 and max = 64'''


class Password(graphene.String):
    '''GraphQL string type with min length = 6 and max = 64'''


class Email(graphene.String):
    '''GraphQL string that represent valid email address'''