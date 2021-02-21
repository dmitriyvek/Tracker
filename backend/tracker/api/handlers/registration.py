from aiohttp.web import json_response, HTTPBadRequest, HTTPCreated
from sqlalchemy.sql import or_, select

from .base import BaseView
from tracker.api.schema import UserRegistrationSchema
from tracker.api.services import validate_input, generate_password_hash
from tracker.db.schema import User


class RegistrationView(BaseView):
    URL_PATH = '/auth/signup'

    async def post(self):
        data = await self.request.text()
        data = validate_input(data, UserRegistrationSchema)

        query = select([User.c.id]).where(or_(
            User.c.username == data['username'],
            User.c.email == data['email']
        ))
        result = await self.db.query(query)
        if len(result):
            error_message = {
                'status': 'fail',
                'message': 'User with given username or email is already exist.'
            }
            raise HTTPBadRequest(reason=error_message,
                                 content_type='application/json')

        data['password'] = generate_password_hash(data['password'])
        await self.db.execute(User.insert().values(data))

        response_data = {
            'status': 'success',
        }
        return json_response(data=response_data, status=HTTPCreated.status_code)
