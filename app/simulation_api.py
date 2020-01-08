from aiohttp import web
from aiohttp_jinja2 import template

from app.service.auth_svc import check_authorization


class SimulationApi:

    def __init__(self, services):
        self.services = services

    @template('mock.html')
    @check_authorization
    async def landing(self, request):
        simulations = set([s.name for s in await self.services.get('data_svc').locate('simulations')])
        loaded_scenario = self.services.get('simulation_svc').loaded_scenario
        return dict(scenarios=simulations, loaded_scenario=loaded_scenario)

    @check_authorization
    async def scenarios(self, request):
        data = dict(await request.json())
        await self.services.get('simulation_svc').apply_scenario(data['scenario'])
        return web.Response()
