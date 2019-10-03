import asyncio
import json
import re
from random import randint


class MockService:

    def __init__(self, services, agents):
        self.agent_svc = services['agent_svc']
        self.data_svc = services['data_svc']
        self.log = services['data_svc'].add_service('simulation_svc', self)
        self.agents = agents

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
                for var in simulated[p]['var']:
                    for val in simulated[p][var]:
                        response = dict(ability_id=simulated['ability_id'], paw=p['paw'], status=p[var][val]['status'],
                                    response=self.agent_svc.encode_string(p[var][val]['response']), var=var, val=val)
                        await self.data_svc.create('sim_response', response)

    async def start_agent(self, agent):
        agent['pid'], agent['ppid'], agent['sleep'] = randint(1000, 10000), randint(1000, 10000), randint(55, 65)
        agent['architecture'] = None
        agent['server'] = 'http://localhost:8888'
        loop = asyncio.get_event_loop()
        loop.create_task(self.run(agent))

    """ PRIVATE """

    async def _extract_vars(self, ability):
        decoded_test = self.agent_svc.decode_bytes(ability['command'])
        variables = re.findall(r'#{(.*?)}', decoded_test, flags=re.DOTALL)
        vars = [x for x in variables if x not in ['server','paw','location','group']]
        search_set = []
        filtering = decoded_test
        for v in vars:
            search_key, filtering = filtering.split("#{" + v + "}", 1)
            search_set.append([v, search_key, filtering[0:3]])
        return search_set

    async def _extract_featured(self, vars, link):
        decoded_command = self.agent_svc.decode_bytes(link['command'])
        extracted = []
        for v in vars:
            extracted.append([v[0], re.findall(r'' + v[1] + '(.*)' +v[2], decoded_command, flags=re.DOTALL)[0]])
        return extracted

    async def _target_response(self, vars, response_object):
        computable = dict()
        for entry in response_object:
            computable[entry['var']] = {entry['val']: entry['response']}
        for v in vars:
            if v[0] in computable:
                if v[1] in computable[v[0]]:
                    return computable[v[0]][v[1]]
        return computable['default']['default']

    async def _get_simulated_response(self, link_id, paw):
        link = (await self.data_svc.get('core_chain', dict(id=link_id)))[0]
        if link['cleanup']:
            return '', 0
        ability = (await self.data_svc.get('core_ability', dict(id=link['ability'])))[0]
        vars = await self._extract_vars(ability)
        sim_response = await self.data_svc.get('sim_response', dict(ability_id=ability['ability_id'], paw=paw))
        if not sim_response:
            return '', 0
        targeted_response = await self._target_response(vars, sim_response)
        if '|SPAWN|' in self.agent_svc.decode_bytes(targeted_response):
            if await self._spawn_new_sim(link):
                return self.agent_svc.encode_string('spawned new agent'), targeted_response[0]['status']
            return self.agent_svc.encode_string('failed to spawn new agent'), 1
        return targeted_response[0]['response'], targeted_response[0]['status']

    async def _spawn_new_sim(self, link):
        filtered = [a for a in self.agents if not a['enabled']]
        run_on = (await self.data_svc.get('core_agent', dict(paw=link['paw'])))[0]
        command_actual = self.agent_svc.decode_bytes(link['command'])
        for agent in filtered:
            box, user = agent['paw'].split('$')
            if user in command_actual and box in command_actual and run_on['platform'] == agent['os']:
                await self.start_agent(agent)
                return True
        return False
