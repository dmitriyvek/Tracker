from aiohttp.web import json_response, HTTPAccepted
from sqlalchemy.sql import select

from .base import BaseView
from tracker.api.schema import UserLoginSchema
from tracker.db.schema import User
from tracker.api.services import validate_input, generate_auth_token, get_user


class LoginView(BaseView):
    URL_PATH = '/auth/login'

    async def post(self):
        data = await self.request.text()
        data = validate_input(data, UserLoginSchema)
        user = await get_user(self.db, data)
        auth_token = generate_auth_token(self.config, user['id'])

        response_data = {
            'status': 'success',
            'auth_token': auth_token,
        }
        return json_response(data=response_data, status=HTTPAccepted.status_code)
