import graphene


class Username(graphene.String):
    '''GraphQL string type with min length = 4 and max = 32'''


class Password(graphene.String):
    '''GraphQL string type with min length = 8 and max = 32'''


class Email(graphene.String):
    '''GraphQL string that represent valid email address'''