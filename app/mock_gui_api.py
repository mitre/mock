from aiohttp_jinja2 import template

from app.utility.base_world import BaseWorld
from app.service.auth_svc import for_all_public_methods, check_authorization


@for_all_public_methods(check_authorization)
class MockGuiApi(BaseWorld):

    def __init__(self, services):
        self.auth_svc = services.get('auth_svc')

    @template('mock.html')
    async def splash(self, request):
        return dict()
