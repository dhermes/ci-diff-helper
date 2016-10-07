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

"""Set of utilities for dealing with Travis CI.

Since Travis only works with GitHub, the commands in this module
are GitHub and ``git`` centric.

This module uses a selection of environment variables to detect
the state of Travis configuration. Among them are:

* ``TRAVIS``: to indicate if running in ``TRAVIS``
* ``TRAVIS_PULL_REQUEST``: to indicate which pull request we are in
  (this is an integer) or to indicate it is a push build
* ``TRAVIS_BRANCH``: to indicate the branch that was pushed (for a
  "push" build) or the branch that a pull request is against

For more details, see the `Travis env docs`_.

.. _Travis env docs: https://docs.travis-ci.com/user/\
                     environment-variables#Default-Environment-Variables
"""

import os


_UNSET = object()  # Sentinel for unset config values.
_IN_TRAVIS_ENV = 'TRAVIS'
_TRAVIS_PR_ENV = 'TRAVIS_PULL_REQUEST'
_TRAVIS_BRANCH_ENV = 'TRAVIS_BRANCH'


def _in_travis():
    """Detect if we are running in Travis.

    :rtype: bool
    :returns: Flag indicating if we are running on Travis.
    """
    return os.getenv(_IN_TRAVIS_ENV) == 'true'


def _travis_pr():
    """Get the current Travis pull request (if any).

    :rtype: int
    :returns: The current pull request ID.
    """
    try:
        return int(os.getenv(_TRAVIS_PR_ENV, ''))
    except ValueError:
        return None


def _travis_branch():
    """Get the current branch of the PR.

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


class Travis(object):
    """Represent Travis state and cache return values."""

    _active = _UNSET
    _base = _UNSET
    _branch = _UNSET
    _pr = _UNSET

    @property
    def active(self):
        """Indicates if currently running in Travis.

        :rtype: bool
        """
        if self._active is _UNSET:
            self._active = _in_travis()
        return self._active

    @property
    def base(self):
        """The ``git`` object that current build is changed against.

        The ``git`` object can be any of a branch name, tag or a commit SHA.

        :rtype: str
        :raises NotImplementedError: If not in a pull request.
        """
        if self._base is _UNSET:
            if self.in_pr:
                self._base = self.branch
            else:
                raise NotImplementedError
        return self._base

    @property
    def branch(self):
        """Indicates if currently running in Travis.

        :rtype: bool
        """
        if self._branch is _UNSET:
            self._branch = _travis_branch()
        return self._branch

    @property
    def in_pr(self):
        """Indicates if currently running in Travis pull request.

        This uses the ``TRAVIS_PULL_REQUEST`` environment variable
        to check if currently in a pull request. Though it doesn't use
        the ``TRAVIS_EVENT_TYPE`` environment variable, checking that
        ``TRAVIS_EVENT_TYPE==pull_request`` would be a perfectly valid
        approach.

        :rtype: bool
        """
        return self.pr is not None

    @property
    def pr(self):
        """The current Travis pull request (if any).

        If there is no active pull request, returns :data:`None`.

        :rtype: int
        """
        if self._pr is _UNSET:
            self._pr = _travis_pr()
        return self._pr
