from annotation_demo import timed
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

    @timed
    def generate_pairs(self, unavailable: set) -> list:
        """Return a list of groups."""

        groups = []

        all_students = sorted(self.roster.keys())

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


def print_sorted(groups: list) -> None:
    """Sort 2D list and print rows."""

    for group in groups:
        group.sort()
    groups.sort()

    for group in groups:
        # print(','.join(group))
        print(' & '.join(group))


def help():
    message = """~~~ Student Lab Partner Script ~~~

An array of student names saved as "[cohort_name].json" in this directory is
required. Replace any spaces with underscores.

To generate new pairs run:
$ python3 pairs -g [cohort_name] [space-separated list of absent students]

To reduce the probability of two students being paired in the future run:
$ python3 pairs -p [cohort_name] [student_1] [student_2]

To see all students and their counts run:
$ python3 pairs -c [cohort_name]"""

    print(message)


def main(flag, cohort_name=None, *names):
    if flag == '-h' or not exists(f'{cohort_name}.json'):
        help()
        return

    if exists(f'{cohort_name}.bin'):
        cohort = Cohort.load(cohort_name)
    else:
        cohort = Cohort(cohort_name)

    if flag == '-g':
        pairs = cohort.generate_pairs(set(names))
        print_sorted(pairs)

    elif flag == '-p':
        cohort.prevent_pairing(*names)
        print(f'Increased counts by {len(cohort.roster)}: {names}')

    elif flag == '-c':
        for student, counts in sorted(cohort.roster.items()):
            print(f'{student}: {counts}\n')

    cohort.save()


if __name__ == '__main__':
    from sys import argv

    if len(argv) < 2:
        help()
    else:
        main(*argv[1:])
