import glob

from plugins.mock.app.c_simulation import Simulation
from plugins.mock.app.simulation_svc import SimulationService

name = 'Mock'
description = 'Simulated agents for testing operations with no external dependencies'
address = None


async def initialize(app, services):
    all_agents = [a for a in services.get('agent_svc').strip_yml('plugins/mock/conf/agents.yml')[0]]
    await services.get('data_svc').apply(collection='simulations')
    await _load_simulations(services)
    simulation_svc = SimulationService(services, all_agents)
    agents = [a for a in all_agents if a['enabled']]
    for a in agents:
        await simulation_svc.start_agent(a)


async def _load_simulations(services):
    for filename in glob.iglob('plugins/mock/conf/sims/*.yml', recursive=True):
        for simulation in services.get('data_svc').strip_yml(filename):
            for r in simulation['responses']:
                for paw in r['paws']:
                    encoded_response = services.get('data_svc').encode_string(paw['response'])
                    await services.get('data_svc').store(
                        Simulation(name=simulation['name'], ability_id=r['ability_id'], paw=paw['paw'],
                                   status=paw.get('status'), response=encoded_response)
                    )
