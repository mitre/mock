import asyncio

from plugins.mock.app.mock_svc import MockService

name = 'Mock'
description = 'A virtual simulation environment for running operations'
address = None


async def initialize(app, services):
    await services['data_svc'].load_data(schema='plugins/%s/mock.sql' % name.lower())
    simulation_svc = MockService(services)
    simulated_responses = [r for r in services.get('agent_svc').strip_yml('plugins/%s/conf/responses.yml' % name.lower())[0]]
    await simulation_svc.load_simulation_results(simulated_responses)
    agents = [a for a in services.get('agent_svc').strip_yml('plugins/%s/conf/config.yml' % name.lower())[0]]
    loop = asyncio.get_event_loop()
    for a in agents:
        loop.create_task(simulation_svc.run(a))
