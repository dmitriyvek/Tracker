from aiohttp.web import json_response, HTTPAccepted

from .base import BaseView
from tracker.api.services import create_blacklist_token
from tracker.api.wrappers import login_required


class LogoutView(BaseView):
    URL_PATH = '/auth/logout'

    @login_required
    async def get(self):
        auth_token = self.request.headers.get('Authorization').split(' ')[1]

        await create_blacklist_token(self.db, auth_token)
        response_data = {
            'status': 'success',
            'message': 'Successfully logged out.'
        }
        return json_response(data=response_data, status=HTTPAccepted.status_code)
