from asyncpgsa import PG
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_urldispatcher import View


class BaseView(View):
    URL_PATH: str

    @property
    def db(self) -> PG:
        return self.request.app['db']

    @property
    def config(self) -> dict:
        return self.request.app['config']
