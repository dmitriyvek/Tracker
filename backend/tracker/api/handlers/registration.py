from aiohttp.web import json_response, HTTPCreated

from .base import BaseView
from tracker.api.schema import UserRegistrationSchema
from tracker.db.schema import User
from tracker.api.services import validate_input, check_if_user_exists, create_user, generate_auth_token


class RegistrationView(BaseView):
    URL_PATH = '/auth/signup'

    async def post(self):
        data = await self.request.text()
        data = validate_input(data, UserRegistrationSchema)
        await check_if_user_exists(self.db, data)

        user = await create_user(self.db, data)
        auth_token = generate_auth_token(self.config, user['id'])
        response_data = {
            'status': 'success',
            'auth_token': auth_token,
            'user': user,
        }
        return json_response(data=response_data, status=HTTPCreated.status_code)
