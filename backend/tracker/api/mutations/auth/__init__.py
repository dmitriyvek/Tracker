import graphene

from .email_confirmation import EmailConfirmation
from .registration import Registration
from .login import Login
from .logout import Logout


class AuthRootMutation(graphene.ObjectType):
    email_confirmation = EmailConfirmation.Field()
    register = Registration.Field()
    login = Login.Field()
    logout = Logout.Field()
