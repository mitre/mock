import glob
import logging

from plugins.mock.app.c_simulation import Simulation
from plugins.mock.app.simulation_api import SimulationApi
from plugins.mock.app.simulation_svc import SimulationService

name = 'Mock'
description = 'Simulated scenarios for testing operations without requiring deployed agents'
address = '/plugin/mock/gui'


async def enable(services):
    logging.getLogger('matplotlib').setLevel(logging.FATAL)
    app = services.get('app_svc').application
    app.router.add_static('/mock', 'plugins/mock/static/', append_version=True)
    await services.get('data_svc').apply(collection='simulations')
    await _load_scenarios(services)

    all_agents = [a for a in services.get('data_svc').strip_yml('plugins/mock/conf/agents.yml')[0]]
    simulation_svc = SimulationService(services, all_agents, loaded_scenario='hunter')
    agents = [a for a in all_agents if a['enabled']]
    for a in agents:
        await simulation_svc.start_agent(a)

    app.router.add_route('GET', '/plugin/mock/gui', SimulationApi(services).landing)
    app.router.add_route('POST', '/plugin/mock/scenario', SimulationApi(services).scenarios)


async def _load_scenarios(services):
    for filename in glob.iglob('plugins/mock/conf/scenarios/*.yml', recursive=True):
        for scenario in services.get('data_svc').strip_yml(filename):
            await _load_advanced_scenario(scenario, services)


async def _load_advanced_scenario(simulation, services):
    for r in simulation['responses']:
        data = services.get('data_svc').strip_yml('plugins/mock/data/{}/{}.yml'.format(simulation['name'],
                                                                                       r['ability_id']))[0]
        for paw in data['paws']:
            for arg in paw['variables']:
                encoded_response = services.get('data_svc').encode_string(arg['response'])
                await services.get('data_svc').store(
                    Simulation(name=simulation['name'], ability_id=r['ability_id'], paw=str(paw['paw']),
                               status=arg.get('status'), response=encoded_response, variable_trait=arg['trait'],
                               variable_value=arg['value'])
                )
