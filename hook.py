from app.utility.base_world import BaseWorld
from plugins.mock.app.simulation_svc import SimulationService

name = 'Mock'
description = 'Simulated scenarios for testing operations without requiring deployed agents'
address = None
access = BaseWorld.Access.RED


async def enable(services):
    all_agents = [a for a in services.get('data_svc').strip_yml('plugins/mock/conf/agents.yml')[0]]
    simulation_svc = SimulationService(services, all_agents)
    agents = [a for a in all_agents if a['enabled']]
    for a in agents:
        await simulation_svc.start_agent(a)
