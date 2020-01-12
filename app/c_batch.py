from datetime import datetime

from app.utility.base_object import BaseObject


class Batch(BaseObject):

    @property
    def unique(self):
        return self.hash('%s' % self.name)

    @property
    def display(self):
        return dict(name=self.name, start=self.start.strftime('%Y-%m-%d %H:%M:%S'),
                    operations=[o.display for o in self.operations])

    def __init__(self, name):
        self.name = name
        self.start = datetime.now()
        self.operations = []

    def store(self, ram):
        existing = self.retrieve(ram['batches'], self.unique)
        if not existing:
            ram['batches'].append(self)
            return self.retrieve(ram['batches'], self.unique)
