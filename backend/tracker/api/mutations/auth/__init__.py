import graphene

from .email_confirmation import RegisterEmailConfirmation
from .registration import Registration
from .login import Login
from .logout import Logout


class AuthRootMutation(graphene.ObjectType):
    email_confirmation = RegisterEmailConfirmation.Field()
    register = Registration.Field()
    login = Login.Field()
    logout = Logout.Field()
