import os
from collections import deque


def split_path_into_components(path):
    """
    Splits a path and returns a list of its constituents.
    E.g.: /totally/random/path => ['totally', 'random', 'path']

    :param path: the path to be split
    :type path: str
    :returns: the list which contains the path components
    """
    head, tail = os.path.split(path)
    if not tail:
        return []

    components = deque()
    components.appendleft(tail)

    path = head

    while path and path != '/':
        head, tail = os.path.split(path)
        components.appendleft(tail)
        path = head

    return list(components)
