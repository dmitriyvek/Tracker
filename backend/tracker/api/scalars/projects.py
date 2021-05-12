import graphene


class Title(graphene.String):
    '''GraphQL string type with min length = 4 and max = 32'''


class Description(graphene.String):
    '''GraphQL string type with min length = 0 and max = 128'''
