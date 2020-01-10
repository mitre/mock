from datetime import datetime

from app.utility.base_object import BaseObject


class Trial(BaseObject):

    @property
    def unique(self):
        return self.hash('%s' % self.name)

    @property
    def display(self):
        return dict(name=self.name, number=self.number, start=self.start.strftime('%Y-%m-%d %H:%M:%S'),
                    operations=[o.display for o in self.operations])

    def __init__(self, name, number):
        self.name = name
        self.number = number
        self.start = datetime.now()
        self.operations = []

    def store(self, ram):
        existing = self.retrieve(ram['trials'], self.unique)
        if not existing:
            ram['trials'].append(self)
            return self.retrieve(ram['trials'], self.unique)
