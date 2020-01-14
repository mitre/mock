import asyncio
import json
import traceback
from random import randint, choice

from app.objects.c_agent import Agent
from app.utility.base_service import BaseService
from plugins.mock.app.fact_generator import FactGenerator


class SimulationService(BaseService):

    def __init__(self, services, agents):
        self.contact_svc = services['contact_svc']
        self.data_svc = services['data_svc']
        self.app_svc = services['app_svc']
        self.log = self.add_service('simulation_svc', self)
        self.agents = agents

    async def run(self, agent):
        """
        Run a simulated agent
        :param agent: as loaded from /mock/conf/agents.yaml and then
         modified locally
        :return:
        """
        while True:
            try:
                await self.contact_svc.handle_heartbeat(agent.paw, agent.platform, agent.server, agent.group,
                                                        agent.host, agent.username, agent.executors, agent.architecture,
                                                        agent.location, agent.pid, agent.ppid,
                                                        await agent.calculate_sleep(), agent.privilege, agent.c2,
                                                        agent.exe_name)
                instructions = json.loads(await self.contact_svc.get_instructions(agent.paw))
                for i in instructions:
                    instruction = json.loads(i)
                    response, status = await self._generate_simulated_response(instruction['id'])
                    await self.contact_svc.save_results(instruction['id'], response, status, agent.pid)
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
                      ppid=randint(1000, 10000), privilege=agent['privilege'], c2=agent['c2'], trusted=True,
                      exe_name=agent['exe_name'])
        await self.data_svc.store(agent)
        agent.sleep_min = agent.sleep_max = randint(15, 25)
        loop = asyncio.get_event_loop()
        loop.create_task(self.run(agent))

    """ PRIVATE """

    async def _generate_simulated_response(self, link_id):
        # case 1: random failure
        status_code = choice(([0] * 15) + [1])
        if status_code == 1:
            return 'failed!', status_code

        # case 2: lateral movement
        link = await self.app_svc.find_link(link_id)
        ability = (await self.data_svc.locate('abilities', match=dict(unique=link.ability.unique)))[0]
        if ability.tactic == 'lateral-movement':
            return self._spawn_new_sim(link), 0

        # case 3: random success
        link.facts = await FactGenerator(ability.parsers).generate()
        return None, status_code

    async def _spawn_new_sim(self, link):
        filtered = [a for a in self.agents if not a['enabled']]
        run_on = (await self.data_svc.locate('agents', match=dict(paw=link.paw)))[0]
        command_actual = self.decode_bytes(link.command)
        for agent in filtered:
            box = agent['host']
            user = agent['username']
            if user in command_actual and box in command_actual and run_on.platform == agent['platform']:
                await self.start_agent(agent)
                return 'new agent started correctly'
        return 'failure to start new agent'
