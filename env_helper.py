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

"""Helps check the state of environment variables.

This is in place for two reasons:

* to give a reference point on each build for what the
  underlying values used were
* to act as a "canary in the coalmine" if the values
  we rely on go away or if new values are added
"""

from __future__ import print_function

import json
import os
import sys


def print_and_check(filter_func, expected):
    """Main script to check environment variables.

    Args:
        filter_func (Callable): A function to filter which variables
            are used.
        expected (frozenset): The set of expected environment variables.
    """
    env_vars = {key: value
                for key, value in os.environ.items()
                if filter_func(key)}
    print(json.dumps(env_vars, indent=2, sort_keys=True))

    vars_found = set(env_vars.keys())
    if not vars_found <= expected:
        print('Encountered unexpected variables', file=sys.stderr)
        for unknown in vars_found - expected:
            print('- {}'.format(unknown), file=sys.stderr)
        sys.exit(1)
