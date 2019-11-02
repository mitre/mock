from aiohttp import web
from aiohttp_jinja2 import template


class SimulationApi:

    def __init__(self, services):
        self.services = services

    @template('mock.html')
    async def landing(self, request):
        await self.services.get('auth_svc').check_permissions(request)
        simulations = set([s.name for s in await self.services.get('data_svc').locate('simulations')])
        plugins = [dict(name=getattr(p, 'name'), address=getattr(p, 'address')) for p in self.services.get('app_svc').get_plugins()]
        loaded_scenario = self.services.get('simulation_svc').loaded_scenario
        return dict(plugins=plugins, scenarios=simulations, loaded_scenario=loaded_scenario)

    async def scenarios(self, request):
        await self.services.get('auth_svc').check_permissions(request)
        data = dict(await request.json())
        await self.services.get('simulation_svc').apply_scenario(data['scenario'])
        return web.Response()
