import random

from app.utility.base_world import BaseWorld


class ResultGenerator(BaseWorld):

    def __init__(self, parser):
        self.parser = parser
        self.facts = {
            'host.file.sensitive': [
                '%s.%s' % (self.generate_name(size=random.randint(1, 20)), random.choice(['txt', 'doc', 'png', 'yml']))
            ]
        }

    async def generate(self, words):
        for parser in self.parser:
            for cfg in parser.parserconfigs:
                for _ in range(random.randint(1, 5)):
                    words.append(await self._gen_value(cfg.source))
                    words.append(await self._gen_value(cfg.target))
        return random.shuffle(words)

    """ PRIVATE """

    async def _gen_value(self, trait):
        if self.facts.get(trait):
            return random.choice(self.facts.get(trait))
        return self.generate_name(size=random.randint(5, 10))
