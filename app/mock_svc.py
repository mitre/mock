import asyncio
import json


class MockService:

    def __init__(self, services):
        self.agent_svc = services['agent_svc']
        self.data_svc = services['data_svc']
        self.log = services['data_svc'].add_service('simulation_svc', self)

    async def run(self, agent):
        while True:
            await self.agent_svc.handle_heartbeat(agent['paw'], agent['os'], agent['server'], agent['group'],
                                                  agent['executors'], agent['architecture'], agent['location'],
                                                  agent['pid'], agent['ppid'], agent['sleep'])
            instructions = json.loads(await self.agent_svc.get_instructions(agent['paw']))
            for i in instructions:
                unpacked = json.loads(i)
                response, status = await self._get_simulated_response(unpacked['id'], agent['paw'])
                await self.agent_svc.save_results(unpacked['id'], response, status)
                await asyncio.sleep(unpacked['sleep'])
            await asyncio.sleep(agent['sleep'])

    async def load_simulation_results(self, simulated_responses):
        for simulated in simulated_responses:
            for p in simulated['paws']:
                response = dict(ability_id=simulated['ability_id'], paw=p['paw'], status=p['status'],
                                response=self.agent_svc.encode_string(p['response']))
                await self.data_svc.create('sim_response', response)

    """ PRIVATE """

    async def _get_simulated_response(self, link_id, paw):
        link = (await self.data_svc.get('core_chain', dict(id=link_id)))[0]
        ability = (await self.data_svc.get('core_ability', dict(id=link['ability'])))[0]
        sim_response = await self.data_svc.get('sim_response', dict(ability_id=ability['ability_id'], paw=paw))
        if not sim_response:
            return '', 0
        return sim_response[0]['response'], sim_response[0]['status']

