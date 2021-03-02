import graphene

from .registration import Registration
from .login import Login
from .logout import Logout


class AuthRootMutation(graphene.ObjectType):
    register = Registration.Field()
    login = Login.Field()
    logout = Logout.Field()
