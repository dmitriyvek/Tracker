from functools import wraps

import aiosmtplib
from aiohttp.web import Application

from tracker.api.errors import APIException
from tracker.api.status_codes import StatusEnum


def send_email_factory(
    app: Application,
) -> None:
    '''
    Decorator for sending mail functions. 
    Wrapped function must accept smtp_client and domain as key word args. 
    '''

    def send_email_decorator(func):

        @wraps(func)
        async def send_email_wrapper(*args, **kwargs):
            config = app['config']

            smtp_client = aiosmtplib.SMTP(
                hostname=config['mail_server'],
                port=config['mail_port'],
                username=config['mail_username'],
                password=config['mail_password'],
                use_tls=config['mail_use_ssl'],
                timeout=config['mail_timeout'],
            )

            host = config['domain_name']
            schema = config['url_schema']
            domain = 'http://localhost:3000' \
                if host == 'localhost' or host == '127.0.0.1' else \
                f'{schema}://{host}'

            try:
                return await func(
                    *args,
                    smtp_client=smtp_client,
                    domain=domain,
                    **kwargs
                )

            except aiosmtplib.SMTPDataError as err:
                if err.code == 550:
                    raise APIException(
                        'Can not send a confirmation email. A letter on given '
                        'email was rejected by smpt server - server consider it spam.'
                        ' If you are using a temporary email address, '
                        'please try registering with a new one.',
                        status=StatusEnum.BAD_GATEWAY.name
                    )

            except aiosmtplib.SMTPRecipientsRefused:
                raise APIException(
                    'Can not send a confirmation email. '
                    ' Smtp server can not send email on give domain.',
                    status=StatusEnum.BAD_GATEWAY.name
                )

            except aiosmtplib.SMTPException as err:
                app['logger'].error(err)
                raise APIException(
                    'Can not send a confirmation email. Action not completed.'
                    ' Please, try again.',
                    status=StatusEnum.BAD_GATEWAY.name
                )

        return send_email_wrapper

    return send_email_decorator
