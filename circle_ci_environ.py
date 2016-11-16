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

"""Checks the state of CircleCI environment variables."""

import env_helper


EXPECTED = frozenset([
    'CI',
    'CIRCLECI',
    'CIRCLECI_PKG_DIR',
    'CIRCLE_ARTIFACTS',
    'CIRCLE_BRANCH',
    'CIRCLE_BUILD_IMAGE',
    'CIRCLE_BUILD_NUM',
    'CIRCLE_BUILD_URL',
    'CIRCLE_COMPARE_URL',
    'CIRCLE_NODE_INDEX',
    'CIRCLE_NODE_TOTAL',
    'CIRCLE_PREVIOUS_BUILD_NUM',
    'CIRCLE_PROJECT_REPONAME',
    'CIRCLE_PROJECT_USERNAME',
    'CIRCLE_PR_NUMBER',
    'CIRCLE_PR_REPONAME',
    'CIRCLE_PR_USERNAME',
    'CIRCLE_REPOSITORY_URL',
    'CIRCLE_SHA1',
    'CIRCLE_TEST_REPORTS',
    'CIRCLE_USERNAME',
    'CI_PULL_REQUEST',
    'CI_PULL_REQUESTS',
    'CI_REPORTS',
])


def filter_func(var_name):
    """Check if the environment variable is relevant.

    Args:
        var_name (str): The name of an environment variable.

    Returns:
        bool: Flag indicating if this variable is ued.
    """
    return 'circle' in var_name.lower() or 'CI' in var_name


if __name__ == '__main__':
    env_helper.print_and_check(filter_func, EXPECTED)
