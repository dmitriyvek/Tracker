from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

import jwt
import aiosmtplib
from aiohttp.web import Application
from asyncpgsa import PG
from sqlalchemy.sql import and_

from tracker.api.errors import APIException
from tracker.api.services.auth import check_if_token_is_blacklisted
from tracker.api.services.roles import RolesData
from tracker.api.services.users import USERS_REQUIRED_FIELDS
from tracker.api.status_codes import StatusEnum
from tracker.db.schema import roles_table, users_table


def generate_role_confirmation_token(
    config: dict,
    email: str,
    project_id: int,
    role: str,
    assign_by: int
) -> bytes:
    '''
    Generates the Role Confirmation Token with the given data.
    '''
    payload = {
        'iat': datetime.utcnow(),
        'email': email,
        'project_id': project_id,
        'role': role,
        'assign_by': assign_by,
    }

    return jwt.encode(
        payload,
        config['secret_key'],
        algorithm='HS256'
    )


@dataclass
class RoleConfTokenPayload:
    email: str
    role: str
    project_id: int
    assign_by: int


async def decode_role_confirmation_token(
    db: PG,
    config: dict,
    token: str,
) -> RoleConfTokenPayload:
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
        email, role, project_id, assign_by = (
            payload.get('email'),
            payload.get('role'),
            payload.get('project_id'),
            payload.get('assign_by')
        )
        if not all([email, role, project_id, assign_by]) or \
                len(payload.keys()) > 5:
            raise jwt.InvalidTokenError('Invalid role confirmation token.')

        await check_if_token_is_blacklisted(db, token)

        return RoleConfTokenPayload(
            email=email,
            role=role,
            project_id=project_id,
            assign_by=assign_by
        )

    except jwt.InvalidTokenError:
        raise APIException(
            'Invalid role confirmation token.',
            status=StatusEnum.BAD_REQUEST.name
        )


async def send_role_confirmation_email(
    app: Application,
    data: RolesData,
    smtp_client: aiosmtplib.SMTP,
    domain: str,
) -> List[str]:
    error_list = []
    config = app['config']

    template = app['jinja_env'].get_template(
        'email/role_confirmation.html'
    )
    async with smtp_client:
        for email in data.email_list:
            message = MIMEMultipart()
            message['From'] = config['mail_username']
            message['To'] = email
            message['Subject'] = 'Tracker role confirmation'

            token = generate_role_confirmation_token(
                config=config,
                email=email,
                role=data.role,
                project_id=data.project_id,
                assign_by=data.assign_by
            )
            confirmation_url = f'{domain}/role/confirmation/{token}'

            content = template.render(
                username=email.split('@')[0],
                title=data.title,
                confirmation_url=confirmation_url
            )
            message.attach(MIMEText(content, 'html', 'utf-8'))

            try:
                await smtp_client.send_message(message)

            except aiosmtplib.SMTPDataError as err:
                if err.code == 550:
                    error_list.append(
                        f'{email}: '
                        'A letter on given email was rejected by '
                        'smpt server - server consider it spam.'
                    )

            except aiosmtplib.SMTPRecipientsRefused:
                error_list.append(
                    f'{email}: '
                    'Smtp server can not send email on give domain.'
                )

            except aiosmtplib.SMTPException as err:
                app['logger'].error(err)
                error_list.append(
                    f'{email}: '
                    'Can not send a confirmation email. '
                    'Role with given email is not created. '
                    'Please, try again.'
                )

    return error_list


async def check_if_user_exists_by_email(
    db: PG, email: str,
) -> dict:
    '''
    Check if account with given email exist.
    If yes returns it. If no returns None.
    '''
    query = users_table.\
        select().\
        with_only_columns([
            *USERS_REQUIRED_FIELDS,
            users_table.c.is_confirmed,
        ]).\
        where(and_(
            users_table.c.email == email,
            users_table.c.is_deleted.is_(False),
        ))

    result = await db.fetchrow(query)
    if result:
        return dict(result)


async def create_role(
    db: PG, data: RoleConfTokenPayload, user_id: int
) -> None:
    '''
    Creates new role with given data and user_id.
    '''
    query = roles_table.\
        insert().\
        values({
            'role': data.role,
            'user_id': user_id,
            'project_id': data.project_id,
            'assign_by': data.assign_by,
        })

    await db.fetchrow(query)
