"""Annotations example from Henry Chen's guest lecture."""

from datetime import datetime


def timed(func):
    def new_func(*args):
        start = datetime.now()

        result = func(*args)

        time = datetime.now() - start
        print(f'function call took {time}')

        return result

    return new_func


@timed
def sum_slice(lst):
    ttl = 0

    for n in lst[::-1]:
        ttl += n

    return ttl


@timed
def sum_reversed(lst):
    ttl = 0

    for n in reversed(lst):
        ttl += n

    return ttl
