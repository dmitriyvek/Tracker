import graphene


class Title(graphene.String):
    '''GraphQL string type with min length = 4 and max = 64'''


class Description(graphene.String):
    '''GraphQL string type with min length = 0 and max = 255'''

