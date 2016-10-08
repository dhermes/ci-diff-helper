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

"""Diff Helper for Continuous Integration (CI) Services.

.. note::

    When configuring your CI environment, it may be useful to set
    the ``GITHUB_OAUTH_TOKEN`` environment variable
    (:data:`~.environment_vars.GH_TOKEN`). By authenticating in
    GitHub API requests, rate-limiting can be avoided. Unauthenticated
    requests will be subject to rate-limiting across the entire
    CI system.
"""

import os
import subprocess

from ci_diff_helper import _utils
from ci_diff_helper.travis import in_travis
from ci_diff_helper.travis import in_travis_pr
from ci_diff_helper.travis import travis_branch


def git_root():
    """Return the root directory of the current ``git`` checkout.

    :rtype: str
    :returns: Filesystem path to ``git`` checkout root.
    """
    return _utils.check_output('git', 'rev-parse', '--show-toplevel')


def get_checked_in_files():
    """Gets a list of files in the current ``git`` repository.

    Effectively runs::

      $ git ls-files ${GIT_ROOT}

    and then finds the absolute path for each file returned.

    :rtype: list
    :returns: List of all filenames checked into.
    """
    root_dir = git_root()
    cmd_output = _utils.check_output('git', 'ls-files', root_dir)

    result = []
    for filename in cmd_output.split('\n'):
        result.append(os.path.abspath(filename))

    return result
