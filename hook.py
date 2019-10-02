from plugins.mock.app.mock_svc import MockService

name = 'Mock'
description = 'Simulated agents for testing operations with no external dependencies'
address = None


async def initialize(app, services):
    await services['data_svc'].load_data(schema='plugins/%s/mock.sql' % name.lower())
    all_agents = [a for a in services.get('agent_svc').strip_yml('plugins/%s/conf/config.yml' % name.lower())[0]]
    simulation_svc = MockService(services, all_agents)
    simulated_responses = [r for r in services.get('agent_svc').strip_yml('plugins/%s/conf/responses.yml' % name.lower())[0]]
    await simulation_svc.load_simulation_results(simulated_responses)
    agents = [a for a in all_agents if a['enabled']]
    for a in agents:
        await simulation_svc.start_agent(a)
