# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run a test application against the HEAD in ci-diff-helper."""

from __future__ import print_function

import ci_diff_helper


PROPERTIES = (
    'active',
    'base',
    'branch',
    'event_type',
    'in_pr',
    'is_merge',
    'merged_pr',
    'pr',
    'slug',
    'tag',
)
"""Our artisanally-crafted list of properties."""
ERROR_TYPES = (
    EnvironmentError,
    KeyError,
    NotImplementedError,
    ValueError,
)
"""Accepted / expected list of errors."""
HELPERS = (
    ci_diff_helper.in_travis,
    ci_diff_helper.in_travis_pr,
    ci_diff_helper.travis_branch,
    ci_diff_helper.get_checked_in_files,
    ci_diff_helper.git_root,
)
"""Helper functions in the base namespace."""
HEADER_SEP = '-' * 40
"""Separator for printing after a header."""
SECTION_SEP = '=' * 40
"""Separator for printing between sections."""


def get_properties(klass):
    """Get the names of all defined ``@property``s on a class.

    :type klass: type
    :param klass: A type to check for properties.

    :rtype tuple:
    :returns: Sorted tuple of `@property` names.
    """
    result = []
    for name in dir(klass):
        klass_attr = getattr(klass, name)
        if isinstance(klass_attr, property):
            result.append(name)
    return tuple(sorted(result))


def main():
    """Main script to test out Travis features."""
    print('Travis() config object:')
    print(HEADER_SEP)
    config = ci_diff_helper.Travis()
    expected_props = get_properties(ci_diff_helper.Travis)
    if expected_props != PROPERTIES:
        raise ValueError('The property list is out of date',
                         'Expected', expected_props,
                         'Actual', PROPERTIES)

    for prop in PROPERTIES:
        try:
            value = getattr(config, prop)
        except ERROR_TYPES as exc:
            value = exc
        print('%22s: %r' % (prop, value))

    print(SECTION_SEP)
    print('Travis (and git) helper functions:')
    print(HEADER_SEP)
    for helper in HELPERS:
        try:
            value = helper()
        except ERROR_TYPES as exc:
            value = exc
        print('%20s(): %r' % (helper.__name__, value))


if __name__ == '__main__':
    main()
