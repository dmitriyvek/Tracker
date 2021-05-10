from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union

import jwt
from aiosmtplib import SMTP
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
        if not payload.get('email') or len(payload.keys()) > 2:
            raise jwt.InvalidTokenError('Invalid email confirmation token.')

        await check_if_token_is_blacklisted(db, token)

        return payload['email']

    except jwt.InvalidTokenError:
        raise APIException(
            'Invalid email confirmation token.',
            status=StatusEnum.BAD_REQUEST.name
        )


async def send_auth_confirmation_email(
    app: Application,
    data: dict,
    smtp_client: SMTP,
    domain: str,
) -> None:
    config = app['config']

    message = MIMEMultipart()
    message['From'] = config['mail_username']
    message['To'] = data['email']
    message['Subject'] = 'Tracker registration confirmation'

    token = generate_email_confirmation_token(
        config=config, email=data['email']
    )
    confirmation_url = f'{domain}/auth/confirmation/{token}'

    template = app['jinja_env'].get_template(
        'email/account_confirmation.html'
    )
    content = template.render(
        username=data['username'],
        confirmation_url=confirmation_url
    )
    message.attach(MIMEText(content, 'html', 'utf-8'))

    async with smtp_client:
        await smtp_client.send_message(message)


async def confirm_email(
    db: PG, email: str, returning: bool = True
) -> Union[dict, None]:
    '''
    Takes an email and verifies an associated account.
    Returns user data if returning param is True (default).
    '''
    query = users_table.\
        update().\
        where(users_table.c.email == email).\
        values(is_confirmed=True)

    if returning:
        query = query.returning(*USERS_REQUIRED_FIELDS)
        user = dict(await db.fetchrow(query))
        return user

    await db.fetchrow(query)
