import glob

from plugins.mock.app.c_simulation import Simulation
from plugins.mock.app.simulation_api import SimulationApi
from plugins.mock.app.simulation_svc import SimulationService

name = 'Mock'
description = 'Simulated scenarios for testing operations with no external dependencies'
address = '/plugin/mock/gui'
directory = None


async def enable(app, services):
    app.router.add_static('/mock', 'plugins/mock/static/', append_version=True)

    all_agents = [a for a in services.get('data_svc').strip_yml('plugins/mock/conf/agents.yml')[0]]
    await services.get('data_svc').apply(collection='simulations')
    await _load_simulations(services)
    simulation_svc = SimulationService(services, all_agents, loaded_scenario='hunter')
    agents = [a for a in all_agents if a['enabled']]
    for a in agents:
        await simulation_svc.start_agent(a)
    app.router.add_route('GET', '/plugin/mock/gui', SimulationApi(services).landing)
    app.router.add_route('POST', '/plugin/mock/scenario', SimulationApi(services).scenarios)


async def _load_simulations(services):
    for filename in glob.iglob('plugins/mock/conf/scenarios/*.yml', recursive=True):
        for simulation in services.get('data_svc').strip_yml(filename):
            if simulation['type'] == 'advanced':
                await _load_advanced_scenario(simulation, services)
            else:
                await _load_basic_scenario(simulation, services)


async def _load_advanced_scenario(simulation, services):
    for r in simulation['responses']:
        for paw in r['paws']:
            encoded_response = services.get('data_svc').encode_string(paw['response'])
            await services.get('data_svc').store(
                Simulation(name=simulation['name'], ability_id=r['ability_id'], paw=str(paw['paw']),
                           status=paw.get('status'), response=encoded_response)
            )


async def _load_basic_scenario(simulation, services):
    all_abilities = [dict(ability_id=a.ability_id, tactic=a.tactic, technique=a.technique_id)
                     for a in await services.get('data_svc').locate('abilities')]
    for r in simulation['responses']:
        for ability in all_abilities:
            if ability['tactic'] == r['tactic'] and ability['technique'] == r['technique']['id']:
                for paw in r['paws']:
                    await services.get('data_svc').store(
                        Simulation(name=simulation['name'], ability_id=ability['ability_id'], paw=str(paw),
                                   status=r['status'], response='')
                    )
