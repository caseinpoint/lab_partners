"""Randomize student lab groups while minimizing repeats.

First, create a JSON file with an array of student names. Then, run this script
with the cohort name as the first argument, and the names of any absent
students as subsequent arguments."""

# this doesn't need to be in main branch anymore, moving to 'legacy' branch

from functools import cached_property
from json import load as js_load
from pickle import load as pk_load
from pickle import dump as pk_dump
from random import sample
from sys import argv
from os.path import exists


class Cohort:
    """A Hackbright cohort object."""

    def __init__(self, cohort_name: str) -> None:
        self.cohort_name = cohort_name
        self.roster = Cohort.load_roster(f'{cohort_name}.json')
        self.previous_groups = set()

    @cached_property
    def max_groups(self):
        """Computed property: maximum number of pairs for roster length."""

        num = len(self.roster)

        # odd rosters have higer max due to 3-groups
        # if num % 2 == 1:
        #     num += 1

        # maximum number of unique pairs formula: n(n-1)/2
        return num * (num - 1) // 2

    @staticmethod
    def load_roster(filename: str) -> set:
        """Load a classroom roster JSON array and return as a set."""

        with open(filename, 'r') as f:
            roster = js_load(f)

        return set(roster)

    @classmethod
    def from_file(cls, cohort_name: str):
        """Load a pickled Cohort and return it."""

        cohort = cls(cohort_name)

        with open(f'{cohort_name}.bin', 'rb') as f:
            cohort.previous_groups = pk_load(f)

        return cohort

    def to_file(self) -> None:
        """Save Cohort previous_groups to pickle file."""

        with open(f'{self.cohort_name}.bin', 'wb') as f:
            pk_dump(self.previous_groups, f)

    @staticmethod
    def shuffle_groups(students: set) -> list:
        """Shuffle set of students and return list of random groups."""

        # randomize available students
        shuffled = sample(population=students, k=len(students))

        groups = []
        # loop over randomized students and make pairs
        for i in range(0, len(shuffled) - 1, 2):
            # append frozenset so order doesn't matter
            groups.append(frozenset([shuffled[i], shuffled[i + 1]]))

        # check if odd number of students
        if len(shuffled) % 2 == 1:
            # reassign last pair to be a group of three
            groups[-1] = frozenset([shuffled[-3], shuffled[-2], shuffled[-1]])

        return groups

    def has_repeats(self, groups: list) -> bool:
        """Return true if any groups exist in previous groups."""

        for group in groups:
            if group in self.previous_groups:
                return True
        return False

    def generate_groups(self, absent_students=set()) -> list:
        """Generate and return a list of random student groups."""

        # available students for grouping using set subtraction
        pool = self.roster - absent_students

        groups = Cohort.shuffle_groups(students=pool)

        # loop until no repeats
        # TODO: this is really inefficient! fix this
        while self.has_repeats(groups):
            # reshuffle the available students
            groups = Cohort.shuffle_groups(pool)

        # check if all possible groups have been made
        if len(self.previous_groups) + len(groups) >= self.max_groups:
            # reset previous groups
            print('max_groups reached, resetting')
            self.previous_groups = set()

        # add all groups to previous pairs
        for group in groups:
            self.previous_groups.add(group)

        return groups


def print_sorted(groups: list) -> None:
    """Print list of groups in a readable way."""

    for i in range(len(groups)):
        # sort partners alphabetically
        groups[i] = sorted(list(groups[i]))
    # sort groups alphabetically by first partner
    groups.sort()

    for group in groups:
        group_str = ' & '.join(group)
        print(group_str)


if __name__ == '__main__':
    # enter cohort_name as argument when running script
    cohort_name = argv[1]

    if exists(f'{cohort_name}.json'):
        if exists(f'{cohort_name}.bin'):
            cohort = Cohort.from_file(cohort_name)
        else:
            cohort = Cohort(cohort_name=cohort_name)

        # enter absent students as arguements following cohort_name
        absent_students = set(argv[2:])

        groups = cohort.generate_groups(absent_students=absent_students)
        print_sorted(groups=groups)

        prev = len(cohort.previous_groups)
        print(f'\ntotal groups: {prev}\nmax. groups: {cohort.max_groups}')

        cohort.to_file()

    else:
        print(f'No file called "{cohort_name}.json"')
