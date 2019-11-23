import asyncio
import json
import traceback

from random import randint

from app.utility.base_service import BaseService
from app.objects.c_agent import Agent


class SimulationService(BaseService):

    def __init__(self, services, agents, loaded_scenario):
        self.data_svc = services['data_svc']
        self.app_svc = services['app_svc']
        self.log = self.add_service('simulation_svc', self)
        self.agents = agents
        self.loaded_scenario = loaded_scenario

    async def apply_scenario(self, scenario):
        """
        Change the simulated scenario
        :param scenario:
        :return:
        """
        self.log.debug('Applying new scenario: %s' % scenario)
        self.loaded_scenario = scenario

    async def run(self, agent):
        """
        Run a simulated agent
        :param agent: as loaded from /mock/conf/agents.yaml and then
         modified locally
        :return:
        """
        while True:
            try:
                c2 = (await self.data_svc.locate('c2', match=dict(name=agent.c2)))[0]
                await c2.handle_heartbeat(agent.paw, agent.platform, agent.server, agent.group, agent.host,
                                          agent.username, agent.executors, agent.architecture, agent.location,
                                          agent.pid, agent.ppid, await agent.calculate_sleep(), agent.privilege,
                                          agent.c2)
                instructions = json.loads(await c2.get_instructions(agent.paw))
                for i in instructions:
                    instruction = json.loads(i)
                    response, status = await self._get_simulated_response(instruction['id'], agent.paw)
                    await c2.save_results(instruction['id'], response, status, agent.pid)
                    await asyncio.sleep(instruction['sleep'])
                await asyncio.sleep(await agent.calculate_sleep())
                agent = (await self.data_svc.locate('agents', match=dict(paw=str(agent.paw))))[0]
            except Exception:
                print(traceback.print_exc())

    async def start_agent(self, agent):
        """
        Create a new agent
        :param agent: as loaded from /mock/conf/agents.yaml
        :return:
        """
        agent = Agent(paw=str(agent['paw']), host=agent['host'], username=agent['username'], group=agent['group'],
                      platform=agent['platform'], server='http://localhost:8888', location=agent['location'],
                      executors=agent['executors'], architecture=None, pid=randint(1000, 10000),
                      ppid=randint(1000, 10000), privilege=agent['privilege'], c2=agent['c2'], trusted=True)
        await self.data_svc.store(agent)
        agent.sleep_min = agent.sleep_max = randint(55, 65)
        loop = asyncio.get_event_loop()
        loop.create_task(self.run(agent))

    """ PRIVATE """

    async def _get_simulated_response(self, link_id, paw):
        link = await self.app_svc.find_link(link_id)
        if link.cleanup:
            return '', 0
        ability = (await self.data_svc.locate('abilities', match=dict(unique=link.ability.unique)))[0]
        search = dict(name=self.loaded_scenario, ability_id=ability.ability_id, paw=paw)
        sim_responses = await self.data_svc.locate('simulations', search)
        if not sim_responses:
            return '', 0
        if '|SPAWN|' in self.decode_bytes(sim_responses[0].response):
            if await self._spawn_new_sim(link):
                return self.encode_string('spawned new agent'), sim_responses[0].status
            return self.encode_string('failed to spawn new agent'), 1
        return sim_responses[0].response, sim_responses[0].status

    async def _spawn_new_sim(self, link):
        filtered = [a for a in self.agents if not a['enabled']]
        run_on = (await self.data_svc.locate('agents', match=dict(paw=link['paw'])))[0]
        command_actual = self.decode_bytes(link['command'])
        for agent in filtered:
            box, user = agent['paw'].split('$')
            if user in command_actual and box in command_actual and run_on['platform'] == agent['os']:
                await self.start_agent(agent)
                return True
        return False
