from aiohttp import web
from aiohttp_jinja2 import template

from app.service.auth_svc import check_authorization


class SimulationApi:

    def __init__(self, services):
        self.services = services
        self.data_svc = services['data_svc']
        # need the next line to make authentication checks work
        self.auth_svc = services['auth_svc']

    @template('mock.html')
    @check_authorization
    async def landing(self, request):
        simulations = set([s.name for s in await self.services.get('data_svc').locate('simulations')])
        loaded_scenario = self.services.get('simulation_svc').loaded_scenario
        hosts = [h.display for h in await self.data_svc.locate('agents')]
        groups = [g for g in set(([h['group'] for h in hosts]))]
        adversaries = [a.display for a in await self.data_svc.locate('adversaries')]
        sources = [s.display for s in await self.data_svc.locate('sources')]
        planners = [p.display for p in await self.data_svc.locate('planners')]
        batches = [t.display for t in await self.data_svc.locate('batches')]
        return dict(scenarios=simulations, adversaries=adversaries, sources=sources, planners=planners,
                    batches=batches, groups=groups, loaded_scenario=loaded_scenario)

    @check_authorization
    async def scenarios(self, request):
        data = dict(await request.json())
        await self.services.get('simulation_svc').apply_scenario(data['scenario'])
        return web.Response()

    @check_authorization
    async def run_batch(self, request):
        data = dict(await request.json())
        batch = await self.services.get('simulation_svc').run_batch(data)
        return web.json_response(batch.display)
