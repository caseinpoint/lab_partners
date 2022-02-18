from collections import Counter
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
        self.roster[students[0]].update({students[1]: 10})
        self.roster[students[1]].update({students[0]: 10})

    def get_least_pairs(self, unavailable=set()):
        lowest_sum = float('inf')
        result = None

        items = list(self.roster.items())
        for student, counts in items:
            if student in unavailable:
                continue

            current_sum = sum(counts.values())

            if current_sum < lowest_sum:
                lowest_sum = current_sum
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

    def find_pair(self, first_student, unavailable=set()):
        # TODO: change this to just pair and create add_partner method
        pair = [first_student]
        students = self._shuffle_common(first_student)

        for student in students:
            if student in unavailable:
                continue

            pair.append(student)
            return pair

    def add_partner(self, group, unavailable=set()):
        sum_counts = Counter()

        for student in group:
            sum_counts.update(self.roster[student])

        for student, _ in reversed(sum_counts.most_common()):
            if student in unavailable or student in group:
                continue

            group.append(student)
            return group

    def generate_pairs(self, unavailable=set()):
        groups = []

        all_students = list(self.roster.keys())
        all_students.sort()

        num_present = len(all_students) - len(unavailable)

        if num_present % 2 == 1:
            first_student = self.get_least_pairs(unavailable)
            first_pair = self.find_pair(first_student, unavailable)
            first_group = self.add_partner(first_pair, unavailable)
            groups.append(first_group)
            unavailable.update(first_group)
            self._update_roster(first_group)

        for student in all_students:
            if student in unavailable:
                continue

            pair = self.find_pair(student, unavailable)
            groups.append(pair)
            unavailable.update(pair)
            self._update_roster(pair)

        return groups


def print_sorted(groups):
    for group in groups:
        group.sort()
    groups.sort()

    for group in groups:
        # print(','.join(group))
        print(' & '.join(group))


# TODO: create main function and if __name__ == '__main__'
# TODO: test with absent students, and prevent_pairing()
# TODO: add doc strings and comments
# TODO: create README
# TODO: create remote and push
