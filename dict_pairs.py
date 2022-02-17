from collections import Counter, OrderedDict
from json import load as js_load
from pickle import load as pk_load
from pickle import dump as pk_dump
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

    def get_least_pairs(self, unavailable=set()):
        least = float('inf')
        result = None

        for student, counts in self.roster.items():
            if student in unavailable:
                continue

            total = sum(counts.values())

            if total < least:
                least = total
                result = student

        return result

    def find_partners(self, first_student, unavailable=set(), size=2):
        partners = [first_student]

        for student, _ in reversed(self.roster[first_student].most_common()):
            if student in unavailable:
                continue

            partners.append(student)

            if len(partners) == size:
                break

        return partners

    def make_groups(self, unavailable=set()):
        groups = []

        all_students = list(self.roster.keys())

        num_present = len(all_students) - len(unavailable)

        if num_present % 2 == 1:
            first_student = self.get_least_pairs(unavailable)
            first_group = self.find_partners(first_student, unavailable, 3)

            groups.append(first_group)
            unavailable.update(first_group)
            self.update_roster(first_group)

        for student in all_students:
            if student in unavailable:
                continue

            group = self.find_partners(student, unavailable)

            groups.append(group)
            unavailable.update(group)
            self.update_roster(group)

        return groups
