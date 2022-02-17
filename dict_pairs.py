from collections import Counter, OrderedDict
from json import load as js_load
from pickle import load as pk_load
from pickle import dump as pk_dump
# from random import choice
# from sys import argv
# from os.path import exists


class Cohort:
    def __init__(self, name, roster=None):
        self.name = name

        if roster is not None:
            self.roster = roster
        else:
            self._generate_roster()

    def _generate_roster(self):
        with open(f'{self.name}.json', 'r') as f:
            names_list = js_load(f)

        self.roster = {}
        for name in names_list:
            self.roster[name] = Counter({n:0 for n in names_list if n != name})

    def save(self):
        with open(f'{self.name}.bin', 'wb') as f:
            pk_dump(obj=self.roster, file=f)

    @classmethod
    def load(cls, name):
        with open(f'{name}.bin', 'rb') as f:
            roster = pk_load(f)

        return cls(name, roster)

    def update_roster(self, names_list):
        for name in names_list:
            other_names = [n for n in names_list if n != name]

            self.roster[name].update(other_names)
