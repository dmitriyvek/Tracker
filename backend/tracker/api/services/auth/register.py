import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bcrypt
import aiosmtplib
from aiohttp.web import Application
from asyncpgsa import PG
from sqlalchemy import select, and_, or_, exists, literal_column

from tracker.api.errors import APIException
from tracker.api.services.auth.base import generate_auth_token
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import users_table


async def check_credentials_duplication(
    db: PG,
    username: str = '',
    email: str = ''
) -> bool:
    '''
    Checks if user with given email or username if already exists
    (takes only username or only email)
    '''

    if username and email:
        raise ValueError('This function takes only username or only email')
    if not (username or email):
        raise ValueError('This function must takes username or email')

    query = users_table.\
        select().\
        with_only_columns([literal_column('1')]).\
        where(users_table.c.is_deleted.is_(False))

    if username:
        query = query.where(users_table.c.username == username)
    else:
        query = query.where(users_table.c.email == email)

    query = select([exists(query)])

    result = await db.fetchval(query)
    return result


def generate_password_hash(password: str, salt_rounds: int = 12) -> str:
    password_bin = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt(salt_rounds))
    encoded = base64.b64encode(hashed)
    return encoded.decode('utf-8')


async def check_if_user_exists(db: PG, data: dict) -> None:
    '''
    Checks if user with given username or email is already exist
    if yes raises 400 error
    '''
    query = select([users_table.c.id]).where(or_(
        and_(
            users_table.c.username == data['username'],
            users_table.c.is_deleted.is_(False)
        ),
        and_(
            users_table.c.email == data['email'],
            users_table.c.is_deleted.is_(False)
        )
    ))
    result = await db.fetchrow(query)
    if result:
        raise APIException(
            'User with given username or email is already exist.',
            status=StatusEnum.BAD_REQUEST.name
        )


async def create_user(db: PG, data: dict) -> dict:
    '''Creates and returns new user'''
    data['password'] = generate_password_hash(data['password'])
    query = users_table.insert().\
        returning(
            users_table.c.id,
            users_table.c.username,
            users_table.c.email
    ).\
        values(data)
    user = dict(await db.fetchrow(query))

    return user


async def send_confirmation_email(
    app: Application,
    data: dict
) -> None:
    config = app['config']

    message = MIMEMultipart()
    message["From"] = config['mail_username']
    message["To"] = data['email']
    message["Subject"] = "Tracker registration confirmation"

    confirmation_token = generate_auth_token(
        config=config, email=data['email']
    )

    template = app['jinja_env'].get_template(
        'email/account_confirmation.html'
    )
    content = template.render(
        username=data['username'],
        confirmation_url='confirmation_url'
    )
    message.attach(MIMEText(content, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            message,
            hostname=config['mail_server'],
            port=config['mail_port'],
            username=config['mail_username'],
            password=config['mail_password'],
            use_tls=config['mail_use_ssl'],
            timeout=10,
        )

    except aiosmtplib.SMTPDataError as err:
        if err.code == 550:
            raise APIException(
                'Can not send a confirmation email. A letter on given '
                'email was rejected by smpt server - server consider it spam.'
                ' If you use temp email try register with new one.',
                status=StatusEnum.BAD_GATEWAY.name
            )

    except aiosmtplib.SMTPException as err:
        raise APIException(
            'Can not send a confirmation email. Registration not completed.'
            ' Please, try again.',
            status=StatusEnum.BAD_GATEWAY.name
        )
