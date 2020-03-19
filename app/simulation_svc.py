import asyncio
import traceback
from random import randint, choice

from app.objects.c_agent import Agent
from app.utility.base_service import BaseService
from plugins.mock.app.result_generator import ResultGenerator


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
                beat = dict(paw=agent.paw)
                _, instructions = await self.contact_svc.handle_heartbeat(**beat)
                for instruction in instructions:
                    response, status = await self._generate_simulated_response(instruction.id)
                    result = dict(id=instruction.id, output=response, status=status, pid=agent.pid)
                    await self.contact_svc.handle_heartbeat(paw=agent.paw, results=[result])
                    await asyncio.sleep(instruction.sleep)
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
                      ppid=randint(1000, 10000), privilege=agent['privilege'], trusted=True,
                      exe_name=agent['exe_name'], sleep_min=30, sleep_max=60, watchdog=0, contact=agent['c2'])
        await self.data_svc.store(agent)
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
        words = []
        for x in range(randint(1, 100)):
            words.append(self.generate_name(size=randint(2, 10)))
        await ResultGenerator(ability.parsers).generate(words)
        return self.encode_string(' '.join(words)), status_code

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
