# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
from collections import deque


def split_path_into_components(path):
    """
    Splits a path and returns a list of its constituents.
    E.g.: /totally/random/path => ['totally', 'random', 'path']

    :param path: the path to be split
    :type path: str
    :returns: the list which contains the path components

    .. note::
        This function is by no means a function which treats all the possible
    constructs. Since we build the paths, we assume the following format. The
    path:
        * has to start with the `/` character if is not empty.
        * it cannot contain double slashes `//`
        * it cannot end with trailing slashes `/`

        Examples of correct paths:
           * ``
           * `/`
           * `/a/b`
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
