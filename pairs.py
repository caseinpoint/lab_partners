#!/usr/bin/env python3

import argparse
from collections import Counter
from json import dump as js_dump
from json import load as js_load
from pickle import load as pk_load
from pickle import dump as pk_dump
from random import shuffle
from os.path import exists
from typing import Iterable


class Cohort:
    """Generates students' lab pairs, and saves pair history to reduce repeats."""

    def __init__(self, name: str, roster: dict = None) -> None:
        self.name = name

        if roster is not None:
            self.roster = roster
        else:
            self._generate_roster()

    def _generate_roster(self) -> None:
        """Load a list of students from JSON and set the instance roster.

        Roster will be a dictionary with a collections.Counter for each student
        to track how many times they've been paired with every other student."""

        with open(f"./data/json/{self.name}.json", "r") as f:
            names = js_load(f)

        self.roster = {}
        for name in names:
            self.roster[name] = Counter({n: 0 for n in names if n != name})

    def save(self) -> None:
        """Cache the student roster."""

        with open(f"./data/pickle/{self.name}.pickle", "wb") as f:
            pk_dump(obj=self.roster, file=f)

    @classmethod
    def load(cls, name: str) -> "Cohort":
        """Load a cached roster and return a new Cohort instance."""

        with open(f"./data/pickle/{name}.pickle", "rb") as f:
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

        lowest_sum = float("inf")
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
        students = Cohort._shuffle_common(self.roster[first_student].most_common())

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


def print_sorted(groups: list, separator: str = " & ") -> None:
    """Sort 2D list and pprint rows."""

    for group in groups:
        group.sort()
    groups.sort()

    for group in groups:
        print(separator.join(group))


def print_csv(cohort: "Cohort") -> None:
    """Print Cohort in .csv format."""

    students = sorted(cohort.roster.keys())
    partners = sorted(cohort.roster.keys(), reverse=True)

    print(",", end="")
    for partner in partners:
        print(partner, end=",")
    print()

    for student in students:
        print(student, end=",")
        for partner in partners:
            if partner == student:
                print("-", end=",")
            else:
                print(cohort.roster[student][partner], end=",")
        print()


def main(args: argparse.Namespace):
    """Run commands based on parsed CLI args."""

    # a JSON file with array of names is required
    json_path = f"./data/json/{args.cohort}.json"
    if not exists(json_path):
        hint = (
            '\n\tHint: do not include ".json" in cohort name.'
            if args.cohort.lower().endswith(".json")
            else ""
        )
        raise FileNotFoundError(
            f'"{json_path}" does not exist for cohort "{args.cohort}"{hint}'
        )

    # load existing Cohort if exists, else create a new one
    if exists(f"./data/pickle/{args.cohort}.pickle"):
        cohort = Cohort.load(args.cohort)
    else:
        cohort = Cohort(args.cohort)

    # handle optional arguments
    if args.generate:
        # create set of absent students, if any
        if args.absent is not None:
            absent = set(args.absent.split(","))
        else:
            absent = set()

        # generate pairs and save counts
        pairs = cohort.generate_pairs(unavailable=absent)
        cohort.save()

        print_sorted(groups=pairs)

    elif args.counts:
        print_csv(cohort=cohort)

    elif args.increment is not None:
        names = args.increment.split(',')
        cohort.update_roster(students=names)
        cohort.save()

        print(f'Pairing counts for {names} incremented by one.')

    elif args.decrement is not None:
        names = args.decrement.split(',')
        cohort.update_roster(students=names, incr=-1)
        cohort.save()

        print(f'Pairing counts for {names} decremented by one.')

    elif args.prevent is not None:
        names = args.decrement.split(',')

        if len(names) != 2:
            raise ValueError('Exactly 2 student names must be provided.')

        cohort.prevent_pairing(student_1=names[0], student_2=names[1])
        cohort.save()

        print(f'Increased the counts for {names} to prevent future pairing.')

    elif args.add is not None:
        if args.add in cohort.roster:
            raise KeyError(f'{args.add} already in cohort.')

        cohort.add_student(new_student=args.add)
        cohort.save()

        # update JSON file
        with open(json_path) as json_read:
            json_lst = js_load(json_read)

        json_lst.append(args.add)
        json_lst.sort()

        with open(json_path, 'w') as json_write:
            js_dump(obj=json_lst, fp=json_write, indent=4)

        print(f'{args.add} added to cohort "{args.cohort}".')

    elif args.remove is not None:
        if args.remove not in cohort.roster:
            raise KeyError(f'{args.remove} not in cohort.')

        cohort.remove_student(student=args.remove)
        cohort.save()

        # update JSON file
        with open(json_path) as json_read:
            json_lst = js_load(json_read)
        json_lst.remove(args.remove)
        with open(json_path, 'w') as json_write:
            js_dump(obj=json_lst, fp=json_write, indent=4)

        print(f'{args.remove} removed from cohort "{args.cohort}".')

    elif args.test:
        # generate several groups of pairs and print, but do not save

        for i in range(len(cohort.roster) + 1):
            # create new set of absent students each iteration (passed by ref)
            if args.absent is not None:
                absent = set(args.absent.split(","))
            else:
                absent = set()

            pairs = cohort.generate_pairs(unavailable=absent)

            print(i)
            print_sorted(groups=pairs, separator=",")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate students' random lab pairs, and save pair history to reduce future repeats."
    )

    parser.add_argument(
        "cohort",
        help="Name of the cohort. A JSON file with that name, containing an array of student names, must exist in `./data/json`. See `./data/json/example.json`.",
    )

    parser.add_argument(
        "-a", "--absent", help="Absent students to exclude from generated pairs. Separate names with commas."
    )

    # options must be one of the following
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-g", "--generate", help="Generate lab pairs.", action="store_true"
    )
    group.add_argument(
        "-c",
        "--counts",
        help="Show current counts for all students in CSV notation.",
        action="store_true",
    )
    group.add_argument(
        "-i",
        "--increment",
        help="Increment the counts for a group of students by one. Separate names with commas.",
    )
    group.add_argument(
        "-d",
        "--decrement",
        help="Decrement the counts for a group of students by one. Separate names with commas.",
    )
    group.add_argument(
        "-p",
        "--prevent",
        help="Prevent the future pairing of 2 students. Separate names with a comma.",
    )
    group.add_argument("--add", help="Add a student name to the roster.")
    group.add_argument("--remove", help="Remove a student name from the roster.")
    group.add_argument(
        "--test",
        help="Generate several groups of pairs without saving counts.",
        action="store_true",
    )

    args = parser.parse_args()
    main(args)
