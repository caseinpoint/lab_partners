from random import shuffle
from sys import argv

STUDENTS = ['Alex', 'Bella', 'Charlotte', 'J', 'Lindsey', 'Lisa',
            'Mehayla', 'Nalisha', 'Rachel', 'Sharon', 'Shosh', 'Sisi',
            'Stephanie', 'Tyricha']

# get absent students from argv
students_absent = set()
if len(argv) > 1:
    for i in range(1, len(argv)):
        students_absent.add(argv[i])

students_present = [s for s in STUDENTS if s not in students_absent]

shuffle(students_present)

pairs = []

while len(students_present) >= 2:
    pairs.append([students_present.pop(), students_present.pop()])

# if there's an odd number, add the last student left to the last pair
if len(students_present) > 0:
    pairs[-1].append(students_present.pop())

for pair in pairs:
    print('    '.join(pair))
