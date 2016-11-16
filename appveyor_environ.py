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

"""Checks the state of AppVeyor environment variables."""

import env_helper


EXPECTED = frozenset([
    'APPVEYOR',
    'APPVEYOR_ACCOUNT_NAME',
    'APPVEYOR_API_URL',
    'APPVEYOR_BUILD_FOLDER',
    'APPVEYOR_BUILD_ID',
    'APPVEYOR_BUILD_NUMBER',
    'APPVEYOR_BUILD_VERSION',
    'APPVEYOR_JOB_ID',
    'APPVEYOR_JOB_NAME',
    'APPVEYOR_PROJECT_ID',
    'APPVEYOR_PROJECT_NAME',
    'APPVEYOR_PROJECT_SLUG',
    'APPVEYOR_REPO_BRANCH',
    'APPVEYOR_REPO_COMMIT',
    'APPVEYOR_REPO_COMMIT_AUTHOR',
    'APPVEYOR_REPO_COMMIT_AUTHOR_EMAIL',
    'APPVEYOR_REPO_COMMIT_MESSAGE',
    'APPVEYOR_REPO_COMMIT_MESSAGE_EXTENDED',
    'APPVEYOR_REPO_COMMIT_TIMESTAMP',
    'APPVEYOR_REPO_NAME',
    'APPVEYOR_REPO_PROVIDER',
    'APPVEYOR_REPO_SCM',
    'APPVEYOR_REPO_TAG',
    'APPVEYOR_URL',
    'CI',
])


def filter_func(var_name):
    """Check if the environment variable is relevant.

    Args:
        var_name (str): The name of an environment variable.

    Returns:
        bool: Flag indicating if this variable is ued.
    """
    return 'appveyor' in var_name.lower() or 'CI' in var_name


if __name__ == '__main__':
    env_helper.print_and_check(filter_func, EXPECTED)
