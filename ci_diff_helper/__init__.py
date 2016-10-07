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

"""Diff Helper for Continuous Integration (CI) Services."""

import os
import subprocess

from ci_diff_helper import _utils
from ci_diff_helper import travis


_TRAVIS_PR_ENV = 'TRAVIS_PULL_REQUEST'
_TRAVIS_BRANCH_ENV = 'TRAVIS_BRANCH'


def in_travis():
    """Detect if we are running in Travis.

    :rtype: bool
    :returns: Flag indicating if we are running on Travis.
    """
    return travis.Travis().active


def in_travis_pr():
    """Detect if we are running in a pull request on Travis.

    .. _Travis env docs: https://docs.travis-ci.com/user/\
                         environment-variables\
                         #Default-Environment-Variables

    See `Travis env docs`_.

    .. note::

        This assumes we already know we are running in Travis.

    :rtype: bool
    :returns: Flag indicating if we are in a pull request on Travis.
    """
    # NOTE: We're a little extra cautious and make sure that the
    #       PR environment variable is an integer.
    try:
        int(os.getenv(_TRAVIS_PR_ENV, ''))
        return True
    except ValueError:
        return False


def travis_branch():
    """Get the current branch of the PR.

    .. _Travis env docs: https://docs.travis-ci.com/user/\
                         environment-variables\
                         #Default-Environment-Variables

    See `Travis env docs`_.

    .. note::

        This assumes we already know we are running in Travis
        during a PR.

    :rtype: str
    :returns: The name of the branch the current pull request is
              changed against.
    :raises OSError: if the ``_TRAVIS_BRANCH_ENV`` environment variable
                     isn't set during a pull request build.
    """
    try:
        return os.environ[_TRAVIS_BRANCH_ENV]
    except KeyError:
        msg = ('Pull request build does not have an '
               'associated branch set (via %s)') % (_TRAVIS_BRANCH_ENV,)
        raise OSError(msg)


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
