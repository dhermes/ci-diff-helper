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

import json

import ci_diff_helper


PROPERTIES_MAP = {
    'AppVeyor': (
        'active',
        'branch',
        'is_merge',
        'provider',
        'tag',
    ),
    'CircleCI': (
        'active',
        'branch',
        'in_pr',
        'is_merge',
        'pr',
        'provider',
        'repo_url',
        'tag',
    ),
    'Travis': (
        'active',
        'base',
        'branch',
        'event_type',
        'in_pr',
        'is_merge',
        'merged_pr',
        'pr',
        'repo_url',
        'slug',
        'tag',
    ),
}
"""Our artisanally-crafted property lists."""
ERROR_TYPES = (
    OSError,
    KeyError,
    NotImplementedError,
    ValueError,
)
"""Accepted / expected list of errors."""
HELPERS = (
    ci_diff_helper.get_checked_in_files,
    ci_diff_helper.git_root,
)
"""Helper functions in the base namespace."""
HEADER_SEP = '-' * 40
"""Separator for printing after a header."""
SECTION_SEP = '=' * 40
"""Separator for printing between sections."""


def get_properties(config):
    """Get the names of all defined ``@property``s on a class.

    Args:
        config (ci_diff_helper._config_base.Config): A config object.

    Returns:
        tuple: Sorted tuple of `@property` names.

    Raises:
        KeyError: If the class does not have an expected property map.
        ValueError: If the property map doesn't agree with the
            current ``config``.
    """
    klass = type(config)  # NOTE: This assumes new-style classes.

    try:
        expected_props = PROPERTIES_MAP[klass.__name__]
    except KeyError:
        raise KeyError('No property map for class', klass)

    result = []
    for name in dir(klass):
        klass_attr = getattr(klass, name)
        if isinstance(klass_attr, property):
            result.append(name)

    result = tuple(sorted(result))
    if expected_props != result:
        raise ValueError('The property list is out of date',
                         'Expected', expected_props,
                         'Actual', result)

    return result


def main():
    """Main script to test out CI features."""
    config = ci_diff_helper.get_config()
    print('Config object: {}'.format(config))
    print(HEADER_SEP)

    config_props = get_properties(config)
    for prop in config_props:
        try:
            value = getattr(config, prop)
        except ERROR_TYPES as exc:
            value = exc
        print('{:>10}: {!r}'.format(prop, value))

    print(SECTION_SEP)
    print('git helper functions:')
    print(HEADER_SEP)
    for helper in HELPERS:
        print('{}():'.format(helper.__name__))
        format_str = '{:>20}(): {!r}'
        try:
            value = helper()
        except ERROR_TYPES as exc:
            value = exc
        if isinstance(value, (list, tuple)):
            json_value = json.dumps(value, indent=2)
            print(json_value)
        else:
            print(repr(value))


if __name__ == '__main__':
    main()
