from collections import Counter, OrderedDict
from json import load as js_load
from pickle import load as pk_load
from pickle import dump as pk_dump
from random import shuffle
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

    def _update_roster(self, students):
        for student in students:
            other_students = [s for s in students if s != student]

            self.roster[student].update(other_students)

    def prevent_pairing(self, students):
        pass

    def get_least_pairs(self, unavailable=set()):
        least = float('inf')
        result = None

        items = list(self.roster.items())
        shuffle(items)
        for student, counts in items:
            if student in unavailable:
                continue

            total = sum(counts.values())

            if total < least:
                least = total
                result = student

        return result

    def _shuffle_common(self, student):
        result = []
        common = self.roster[student].most_common()

        for n in range(common[-1][-1], common[0][-1] + 1):
            sub = [s for s, c in common if c == n]
            shuffle(sub)
            result.extend(sub)

        return result

    def find_partners(self, first_student, unavailable=set(), size=2):
        partners = [first_student]

        while len(partners) < size:
            students = self._shuffle_common(partners[-1])

            for student in students:
                if student in unavailable:
                    continue

                partners.append(student)
                unavailable.update(partners)
                break

        return partners

    def make_groups(self, unavailable=set()):
        groups = []

        all_students = list(self.roster.keys())
        # all_students.sort()
        # shuffle(all_students)

        num_present = len(all_students) - len(unavailable)

        if num_present % 2 == 1:
            first_student = self.get_least_pairs(unavailable)
            first_group = self.find_partners(first_student, unavailable, 3)
            groups.append(first_group)
            # unavailable.update(first_group)
            self._update_roster(first_group)

        for student in all_students:
            if student in unavailable:
                continue

            group = self.find_partners(student, unavailable)
            groups.append(group)
            # unavailable.update(group)
            self._update_roster(group)

        return groups


def print_sorted(groups):
    for group in groups:
        group.sort()
    groups.sort()

    for group in groups:
        # print(' & '.join(group))
        print(','.join(group))
