#!/usr/bin/env python3

from collections import Counter
from json import load as js_load
from pickle import load as pk_load
from pickle import dump as pk_dump
from random import shuffle
from os.path import exists
from typing import Iterable


class Cohort:
    """A data structure for storing and generating students' lab pairs."""

    def __init__(self, name: str, roster: dict = None) -> None:
        self.name = name

        if roster is not None:
            self.roster = roster
        else:
            self._generate_roster()

    def _generate_roster(self) -> None:
        """Load a list of students from JSON and set the instance roster.

        Roster will be a dictionary with a collections.Counter for each student
        to track how many times they've been paired with every other student"""

        with open(f'{self.name}.json', 'r') as f:
            names = js_load(f)

        self.roster = {}
        for name in names:
            self.roster[name] = Counter({n: 0 for n in names if n != name})

    def save(self) -> None:
        """Cache the student roster."""

        with open(f'{self.name}.bin', 'wb') as f:
            pk_dump(obj=self.roster, file=f)

    @classmethod
    def load(cls, name: str) -> 'Cohort':
        """Load a cached roster and return a new Cohort instance."""

        with open(f'{name}.bin', 'rb') as f:
            roster = pk_load(f)

        return cls(name, roster)

    def update_roster(self, students: Iterable, incr: int = 1) -> None:
        """Update roster counts for all students in a group."""

        for student in students:
            other_students = {s: incr for s in students if s != student}

            self.roster[student].update(other_students)

    def bulk_update(self, others: Iterable) -> None:
        """Bulk update roster counts.

        Loop over others and add counts for existing students in self.roster.
        """

        for house_name in others:
            other = Cohort.load(house_name)

            for student, counts in other.roster.items():
                if student in self.roster:
                    self.roster[student].update(counts)

    def remove_student(self, student: str) -> None:
        """Remove a student from the roster."""

        self.roster.pop(student, None)

        for student_counter in self.roster.values():
            student_counter.pop(student, None)

    def add_student(self, new_student: str) -> None:
        """Add a new student to the roster."""

        new_counter = Counter()

        for student, student_counts in self.roster.items():
            student_counts.update({new_student: 0})
            new_counter.update({student: 0})

        self.roster[new_student] = new_counter

    def prevent_pairing(self, student_1: str, student_2: str) -> None:
        """Reduce chances of being paired in the future for two students."""

        # TODO: this method works to reduce chances of pairing in future,
        # but also may reduce the chances of being selected for future groups
        # of three for both students. testing needed.

        self.roster[student_1].update({student_2: len(self.roster)})
        self.roster[student_2].update({student_1: len(self.roster)})

    def get_least_pairs(self, unavailable: set) -> str:
        """Return the student with the least amount of past partners.

        If multiple results, return the first encountered."""

        lowest_sum = float('inf')
        result = None

        names_counts = sorted(self.roster.items())
        for student, counts in names_counts:
            if student in unavailable:
                continue

            current_sum = sum(counts.values())

            if current_sum < lowest_sum:
                lowest_sum = current_sum
                result = student

        return result

    @staticmethod
    def _shuffle_common(tuples_list: list) -> list:
        """Shuffle a list of tuples and return a list of strings.

        tuples_list must be a list of tuples, as returned by
        Counter.most_common().  Returns list of shuffled names in ascending
        order by count."""

        result = []

        # loop over all counts in list
        for n in range(tuples_list[-1][-1], tuples_list[0][-1] + 1):
            # create list of names with that count
            sub_group = [s for s, c in tuples_list if c == n]

            shuffle(sub_group)
            result.extend(sub_group)

        return result

    def find_pair(self, first_student: str, unavailable: set) -> list:
        """Return a pair of students.

        Finds an available pair for first_student based on lowest shared
        count."""

        pair = [first_student]
        students = Cohort._shuffle_common(
            self.roster[first_student].most_common())

        for student in students:
            if student in unavailable:
                continue

            pair.append(student)
            return pair

    def add_partner(self, group: list, unavailable: set) -> list:
        """Find a valid partner and append it to group.

        Finds an available partner based on the lowest sum of counts for the
        entire group."""

        sum_counts = Counter()

        for student in group:
            sum_counts.update(self.roster[student])

        students = Cohort._shuffle_common(sum_counts.most_common())
        for student in students:
            if student in unavailable or student in group:
                continue

            group.append(student)
            return group

    def generate_pairs(self, unavailable: set) -> list:
        """Return a list of groups."""

        groups = []

        # all_students = sorted(self.roster.keys(), reverse=True)
        all_students = list(self.roster.keys())
        shuffle(all_students)

        num_present = len(all_students) - len(unavailable)

        # Check if odd number of students
        if num_present % 2 == 1:
            # Student w/ least pairs indicates least amount of times in group
            # of 3, or has absences. Select them for group of 3 this time.
            first_student = self.get_least_pairs(unavailable)
            first_pair = self.find_pair(first_student, unavailable)
            first_group = self.add_partner(first_pair, unavailable)
            groups.append(first_group)

            unavailable.update(first_group)
            self.update_roster(first_group)

        for student in all_students:
            if student in unavailable:
                continue

            pair = self.find_pair(student, unavailable)
            groups.append(pair)

            unavailable.update(pair)
            self.update_roster(pair)

        return groups


def print_sorted(groups: list, separator: str = ' & ') -> None:
    """Sort 2D list and pprint rows."""

    for group in groups:
        group.sort()
    groups.sort()

    for group in groups:
        print(separator.join(group))


def script_help() -> None:
    """Print a help message."""

    MESSAGE = """~~~ Student Lab Partner Script ~~~

An array of student names saved in this directory as "<cohort_name>.json" is
required. Replace any spaces in their names with underscores. See example.json
included in repo.

To generate new pairs:
$ python3 pairs.py -g <cohort_name> <space-separated list of absent students>

To increment/decrement the counts for an individual group:
$ python3 pairs.py <-i/-d> <cohort_name> <space-separated list of students>

In the case of separate files for houses, update the counts of the full cohort
with the counts from houses:
$ python3 pairs.py -u <cohort_name> <space-separated list of house names>

To reduce the probability of two students being paired in the future:
$ python3 pairs.py -p <cohort_name> <student_1> <student_2>

To remove a student from the roster:
$ python3 pairs.py -r <cohort_name> <student>
(It is recommended to remove the student from <cohort_name>.json, as well)

To add a student to the roster:
$ python3 pairs.py -a <cohort_name> <student>
(It is recommended to add the student to <cohort_name>.json, as well)

To see all students and their counts (formated for .csv):
$ python3 pairs.py -c <cohort_name>"""

    print(MESSAGE)


def main(flag: str, cohort_name: str = None, *names) -> None:
    """Parse CLI arguments and run commands."""

    if flag == '-h' or not exists(f'{cohort_name}.json'):
        script_help()
        return

    if exists(f'{cohort_name}.bin'):
        cohort = Cohort.load(cohort_name)
    else:
        cohort = Cohort(cohort_name)

    # generate pairs
    if flag == '-g':
        absent = set(names)
        pairs = cohort.generate_pairs(absent)
        cohort.save()
        print_sorted(pairs)

    # increment the counts for a group
    elif flag == '-i':
        cohort.update_roster(names)
        cohort.save()
        print(f'Incremented counts for {names} by one.')

    # decrement the counts for a group
    elif flag == '-d':
        cohort.update_roster(names, incr=-1)
        cohort.save()
        print(f'Decremented counts for {names} by one.')

    # update main cohort count with house(s) count
    elif flag == '-u':
        cohort.bulk_update(names)
        cohort.save()
        print(f'Updated cohort counts with counts from {names}.')

    # prevent future pairing
    elif flag == '-p':
        if len(names) != 2:
            script_help()

        else:
            cohort.prevent_pairing(*names)
            cohort.save()
            print(f'Increased counts by {len(cohort.roster)}: {names}.')

    # remove student from roster
    elif flag == '-r':
        if len(names) != 1:
            script_help()

        else:
            cohort.remove_student(names[0])
            cohort.save()
            print(f'Revomed {names[0]} from the roster.')

    # add student to roster
    elif flag == '-a':
        if len(names) != 1:
            script_help()

        else:
            cohort.add_student(names[0])
            cohort.save()
            print(f'Added {names[0]} to the roster.')

    # show all counts
    elif flag == '-c':
        for student, counts in sorted(cohort.roster.items()):
            print(student, end=', ')
            for pair, count in sorted(counts.items(),
                                      key=lambda t: t[1],
                                      reverse=True):
                print(f'{pair}, {count}', end=', ')
            print()


    # generate many groups w/out saving for testing purposes
    elif flag == '--test':
        for i in range(len(cohort.roster) + 1):
            print(i)
            absent = set(names)
            pairs = cohort.generate_pairs(absent)
            print_sorted(pairs, separator=',')


if __name__ == '__main__':
    from sys import argv

    if len(argv) < 2:
        script_help()
    else:
        main(*argv[1:])
