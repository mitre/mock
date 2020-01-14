import random

from app.objects.c_fact import Fact
from app.utility.base_world import BaseWorld


class FactGenerator(BaseWorld):

    def __init__(self, parser):
        self.parser = parser
        self.facts = {
            'host.user.name': [
                self.generate_name(size=random.randint(2, 12))
            ],
            'host.file.sensitive': [
                '%s.%s' % (self.generate_name(size=random.randint(1, 20)), random.choice(['txt', 'doc', 'png']))
            ]
        }

    async def generate(self):
        generated_facts = []
        for parser in self.parser:
            for cfg in parser.parserconfigs:
                if cfg.source:
                    generated_facts.append(Fact(trait=cfg.source, value=await self._gen_value(cfg.source)))
                if cfg.target:
                    generated_facts.append(Fact(trait=cfg.target, value=await self._gen_value(cfg.target)))
        return generated_facts

    """ PRIVATE """

    async def _gen_value(self, trait):
        return self.facts.get(trait, random.choice([self.generate_name(size=random.randint(5, 10))]))
