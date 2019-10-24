from app.objects.base_object import BaseObject


class Simulation(BaseObject):

    @property
    def unique(self):
        return self.hash('%s%s%s' % (self.name, self.ability_id, self.paw))

    @property
    def display(self):
        return dict(name=self.name, ability_id=self.ability_id, paw=self.paw, status=self.status, response=self.response)

    def __init__(self, name, ability_id, paw, status, response):
        self.name = name
        self.ability_id = ability_id
        self.paw = paw
        self.status = status
        self.response = response

    def store(self, ram):
        existing = self.retrieve(ram['simulations'], self.unique)
        if not existing:
            ram['simulations'].append(self)
            return self.retrieve(ram['simulations'], self.unique)
