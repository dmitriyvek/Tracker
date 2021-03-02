from graphene.utils.str_converters import to_camel_case


class APIException(Exception):
    '''Excpetion that adds all key word arguments to self context'''

    def __init__(self, message, **kwargs):
        if kwargs:
            self.context = {to_camel_case(
                key): value for key, value in kwargs.items()}

        super().__init__(message)
