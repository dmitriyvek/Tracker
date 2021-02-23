from .registration import RegistrationView
from .login import LoginView
from .logout import LogoutView


HANDLERS = (
    RegistrationView,
    LoginView,
    LogoutView,
)
