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
    (:attr:`.environment_vars.GH_TOKEN`). By authenticating in
    GitHub API requests, rate-limiting can be avoided. Unauthenticated
    requests will be subject to rate-limiting across the entire
    CI system.
"""

import os
import subprocess

from ci_diff_helper import _utils
from ci_diff_helper import travis


def in_travis():
    """Detect if we are running in Travis.

    See the :class:`.Travis` class for a
    more comprehensive way to determine the Travis configuration,
    with caching enabled. In particular, for this method, see
    :attr:`.Travis.active`.

    :rtype: bool
    :returns: Flag indicating if we are running on Travis.
    """
    return travis.Travis().active


def in_travis_pr():
    """Detect if we are running in a pull request on Travis.

    See the :class:`.Travis` class for a
    more comprehensive way to determine the Travis configuration,
    with caching enabled. In particular, for this method, see
    :attr:`.Travis.in_pr`.

    :rtype: bool
    :returns: Flag indicating if we are in a pull request on Travis.
    """
    return travis.Travis().in_pr


def travis_branch():
    """Get the current branch of the PR.

    See the :class:`.Travis` class for a
    more comprehensive way to determine the Travis configuration,
    with caching enabled. In particular, for this method, see
    :attr:`.Travis.branch`.

    .. note::

        This assumes we already know we are running in Travis
        during a PR.

    :rtype: str
    :returns: The name of the branch the current pull request is
              changed against.
    """
    return travis.Travis().branch


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
