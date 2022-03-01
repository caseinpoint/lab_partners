# from annotation_demo import timed
from collections import Counter
from json import load as js_load
from pickle import load as pk_load
from pickle import dump as pk_dump
from random import shuffle
from os.path import exists


class Cohort:
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
            names_list = js_load(f)

        self.roster = {}
        for name in names_list:
            self.roster[name] = Counter({n:0 for n in names_list if n != name})

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

    def _update_roster(self, students) -> None:
        """Update roster counts for all students in a group."""

        for student in students:
            other_students = [s for s in students if s != student]

            self.roster[student].update(other_students)

    def prevent_pairing(self, student_1, student_2) -> None:
        """Reduce chances of being paired in the future for two students."""

        # FIXME: this method works to reduce chances of pairing in future,
        # but also will reduce the chances of being selected for future groups
        # of three. refactor needed

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
        """Shuffle a list of tuples and return a list of names.

        tuples_list must be a list of tuples, as returned by
        Counter.most_common().  Returns list in ascending order by count."""

        result = []

        for n in range(tuples_list[-1][-1], tuples_list[0][-1] + 1):
            sub_group = [s for s, c in tuples_list if c == n]
            shuffle(sub_group)
            result.extend(sub_group)

        return result

    def find_pair(self, first_student: str, unavailable: set) -> list:
        """Return a pair of students.

        Finds an available pair for first_student based on lowest shared
        count."""

        pair = [first_student]
        # students = Cohort._shuffle_common(
        #     self.roster[first_student].most_common())

        # for student in students:
        for student, _ in reversed(self.roster[first_student].most_common()):
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

        # students = Cohort._shuffle_common(sum_counts.most_common())
        # for student in students:
        for student, _ in reversed(sum_counts.most_common()):
            if student in unavailable or student in group:
                continue

            group.append(student)
            return group

    # @timed
    def generate_pairs(self, unavailable: set) -> list:
        """Return a list of groups."""

        groups = []

        all_students = sorted(self.roster.keys(), reverse=True)
        # all_students = list(self.roster.keys())
        # shuffle(all_students)

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
            self._update_roster(first_group)

        for student in all_students:
            if student in unavailable:
                continue

            pair = self.find_pair(student, unavailable)
            groups.append(pair)

            unavailable.update(pair)
            self._update_roster(pair)

        return groups


def print_sorted(groups: list, separator: str = ' & ') -> None:
    """Sort 2D list and pprint rows."""

    for group in groups:
        group.sort()
    groups.sort()

    for group in groups:
        print(separator.join(group))


def help() -> None:
    message = """~~~ Student Lab Partner Script ~~~

An array of student names saved as "[cohort_name].json" in this directory is
required. Replace any spaces in their names with underscores.

To generate new pairs run:
$ python3 pairs.py -g [cohort_name] [space-separated list of absent students]

To reduce the probability of two students being paired in the future run:
$ python3 pairs.py -p [cohort_name] [student_1] [student_2]

To see all students and their counts run:
$ python3 pairs.py -c [cohort_name]"""

    print(message)


# @timed
def main(flag: str, cohort_name: str = None, *names) -> None:
    if flag == '-h' or not exists(f'{cohort_name}.json'):
        help()
        return

    if exists(f'{cohort_name}.bin'):
        cohort = Cohort.load(cohort_name)
    else:
        cohort = Cohort(cohort_name)

    if flag == '-g':
        absent = set(names)
        pairs = cohort.generate_pairs(absent)
        print_sorted(pairs)
        cohort.save()

    elif flag == '-p':
        if len(names) != 2:
            help()
        else:
            cohort.prevent_pairing(*names)
            print(f'Increased counts by {len(cohort.roster)}: {names}')
            cohort.save()

    elif flag == '-c':
        for student, counts in sorted(cohort.roster.items()):
            print(f'{student}: {counts}, sum: {sum(counts.values())}\n')

    # for testing purposes
    elif flag == '-t':
        for _ in range(len(cohort.roster) + 1):
            absent = set(names)
            pairs = cohort.generate_pairs(absent)
            print_sorted(pairs, separator=',')


if __name__ == '__main__':
    from sys import argv

    if len(argv) < 2:
        help()
    else:
        main(*argv[1:])
