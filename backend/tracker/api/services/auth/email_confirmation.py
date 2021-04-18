from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
import jwt
from aiohttp.web import Application
from asyncpgsa import PG

from tracker.api.errors import APIException
from tracker.api.services.auth import check_if_token_is_blacklisted
from tracker.api.services.users import USERS_REQUIRED_FIELDS
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import users_table


def generate_email_confirmation_token(
    config: dict,
    email: str,
) -> bytes:
    '''
    Generates the Email Confirmation Token with the given email.
    '''
    payload = {
        'iat': datetime.utcnow(),
        'email': email
    }

    return jwt.encode(
        payload,
        config['secret_key'],
        algorithm='HS256'
    )


async def decode_email_confirmation_token(
    db: PG,
    config: dict,
    token: str,
) -> str:
    '''
    Decodes given email confirmation token and 
    returns email or raise 400 if token is invalid.
    '''
    try:
        payload = jwt.decode(
            token,
            config.get('secret_key'),
            algorithms=['HS256'],
            options={
                'require_exp': False,
                'require_iat': True,
                'verify_exp': False,
                'verify_iat': True,
                'verify_signature': True,
            }
        )
        if not payload.get('email'):
            raise jwt.InvalidTokenError('Invalid email confirmation token.')

        await check_if_token_is_blacklisted(db, token)

        return payload['email']

    except jwt.InvalidTokenError:
        raise APIException(
            'Invalid email confirmation token.',
            status=StatusEnum.BAD_REQUEST.name
        )


async def send_confirmation_email(
    app: Application,
    data: dict
) -> None:
    config = app['config']

    message = MIMEMultipart()
    message['From'] = config['mail_username']
    message['To'] = data['email']
    message['Subject'] = 'Tracker registration confirmation'

    confirmation_token = generate_email_confirmation_token(
        config=config, email=data['email']
    )
    print(confirmation_token)

    template = app['jinja_env'].get_template(
        'email/account_confirmation.html'
    )
    content = template.render(
        username=data['username'],
        confirmation_url=confirmation_token
    )
    message.attach(MIMEText(content, 'html', 'utf-8'))

    try:
        await aiosmtplib.send(
            message,
            hostname=config['mail_server'],
            port=config['mail_port'],
            username=config['mail_username'],
            password=config['mail_password'],
            use_tls=config['mail_use_ssl'],
            timeout=config['mail_timeout'],
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

    except aiosmtplib.SMTPException as err:
        raise APIException(
            'Can not send a confirmation email. Registration not completed.'
            ' Please, try again.',
            status=StatusEnum.BAD_GATEWAY.name
        )


async def confirm_email(db: PG, email: str) -> dict:
    '''
    Takes an email and verifies an associated account.
    Returns user data.
    '''
    query = users_table.\
        update().\
        where(users_table.c.email == email).\
        values(is_confirmed=True).\
        returning(*USERS_REQUIRED_FIELDS)

    user = dict(await db.fetchrow(query))
    return user
