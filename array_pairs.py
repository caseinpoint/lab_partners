from functools import cached_property
from json import load as js_load
from math import inf
from pickle import load as pk_load
from pickle import dump as pk_dump
from random import choice
from sys import argv
from os.path import exists


def find_mins(lst):
    if len(lst) == 0:
        return []

    smallest = lst[0]
    indexes = [0]

    for i in range(1, len(lst)):
        if lst[i] == smallest:
            indexes.append(i)

        elif lst[i] < smallest:
            smallest = lst[i]
            indexes = [i]

    return indexes


class Cohort:
    def __init__(self, name, array=None):
        self.name = name

        if array is None:
            self._build_array()
        else:
            self.array = array

    @cached_property
    def students(self):
        with open(f'{self.name}.json', 'r') as f:
            roster = js_load(f)

        return roster

    @classmethod
    def from_file(cls, name):
        with open(f'{name}.bin', 'rb') as f:
            array = pk_load(f)

        return cls(name, array)

    def to_file(self):
        with open(f'{self.name}.bin', 'wb') as f:
            pk_dump(self.array, f)

    def _build_array(self):
        self.array = []

        for r in range(len(self.students)):
            row = []

            for c in range(len(self.students)):
                if c == r:
                    row.append(inf)
                else:
                    row.append(0)

            self.array.append(row)

    def find_absents(self, absent_students):
        indexes = []

        for student in absent_students:
            try:
                indexes.append(self.students.index(student))
            except ValueError:
                pass

        return indexes

    def insert_odd(self, pairs, idx):
        pass

    def generate_groups(self, absent_students):
        absents = self.find_absents(absent_students)
