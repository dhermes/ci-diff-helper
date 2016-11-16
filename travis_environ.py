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

"""Checks the state of Travis environment variables."""

import env_helper


EXPECTED = frozenset([
    'TRAVIS',
    'TRAVIS_BRANCH',
    'TRAVIS_BUILD_DIR',
    'TRAVIS_BUILD_ID',
    'TRAVIS_BUILD_NUMBER',
    'TRAVIS_COMMIT',
    'TRAVIS_COMMIT_RANGE',
    'TRAVIS_EVENT_TYPE',
    'TRAVIS_JOB_ID',
    'TRAVIS_JOB_NUMBER',
    'TRAVIS_LANGUAGE',
    'TRAVIS_OS_NAME',
    'TRAVIS_PULL_REQUEST',
    'TRAVIS_PYTHON_VERSION',
    'TRAVIS_REPO_SLUG',
    'TRAVIS_SECURE_ENV_VARS',
    'TRAVIS_TAG',
])


def filter_func(var_name):
    """Check if the environment variable is relevant.

    Args:
        var_name (str): The name of an environment variable.

    Returns:
        bool: Flag indicating if this variable is ued.
    """
    return 'travis' in var_name.lower() or 'CI' in var_name


if __name__ == '__main__':
    env_helper.print_and_check(filter_func, EXPECTED)
