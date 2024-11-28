from typing import Callable, Iterable


class Maybe[T]:
    def __init__(self, val: T = None):
        self.val = val

    def map[U](self, func: Callable[[T], U]) -> "Maybe[U]":
        return self if self.val is None else Maybe(func(self.val))


def find[T](pred: Callable[[T], bool], iterable: Iterable[T]) -> Maybe[T]:
    """return first item of iterable that satisfies pred or None if there isn't any"""
    for i in iterable:
        if pred(i):
            return Maybe(i)
    return Maybe()
