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
the state of Travis configuration. See
:mod:`~ci_diff_helper.environment_vars` for more details.
"""

import os

import enum

from ci_diff_helper import _github
from ci_diff_helper import _utils
from ci_diff_helper import environment_vars as env


_UNSET = object()  # Sentinel for unset config values.
_RANGE_DELIMITER = '...'


def _in_travis():
    """Detect if we are running in Travis.

    :rtype: bool
    :returns: Flag indicating if we are running on Travis.
    """
    return os.getenv(env.IN_TRAVIS_ENV) == 'true'


def _travis_pr():
    """Get the current Travis pull request (if any).

    :rtype: int
    :returns: The current pull request ID.
    """
    try:
        return int(os.getenv(env.TRAVIS_PR_ENV, ''))
    except ValueError:
        return None


def _travis_branch():
    """Get the current branch of the PR.

    :rtype: str
    :returns: The name of the branch the current pull request is
              changed against.
    :raises EnvironmentError: if the ``TRAVIS_BRANCH`` environment variable
                              isn't set during a pull request build.
    """
    try:
        return os.environ[env.TRAVIS_BRANCH_ENV]
    except KeyError as exc:
        msg = ('Pull request build does not have an '
               'associated branch set (via %s)') % (env.TRAVIS_BRANCH_ENV,)
        raise EnvironmentError(exc, msg)


def _travis_event_type():
    """Get the event type of the current Travis build

    :rtype: :class:`TravisEventType`
    :returns: The type of the current Travis build.
    :raises ValueError: if the ``TRAVIS_EVENT_TYPE`` environment
                        variable is not one of the expected values.
    """
    event_env = os.getenv(env.TRAVIS_EVENT_TYPE_ENV, '')
    try:
        return TravisEventType(event_env)
    except ValueError:
        raise ValueError('Invalid event type', event_env,
                         'Expected one of',
                         [enum_val.name for enum_val in TravisEventType])


def _get_commit_range():
    """Get the Travis commit range from the environment.

    Uses the ``TRAVIS_COMMIT_RANGE`` environment variable and then
    makes sure it can be split into a start and finish commit.

    :rtype: tuple
    :returns: The ``start``, ``finish`` pair from the commit range.
    :raises EnvironmentError: if the ``TRAVIS_COMMIT_RANGE`` does not contain
                              '...' (which indicates a start and end commit)
    """
    commit_range = os.getenv(env.TRAVIS_RANGE_ENV, '')
    try:
        start, finish = commit_range.split(_RANGE_DELIMITER)
        return start, finish
    except ValueError as exc:
        raise EnvironmentError(
            exc, 'Commit range in unexpected format', commit_range)


def _verify_merge_base(start, finish):
    """Verifies that the merge base of a commit range **is** the start.

    :type start: str
    :param start: The start commit in a range.

    :type finish: str
    :param finish: The last commit in a range.

    :raises ValueError: If the merge base is not the start commit
    """
    merge_base = _utils.check_output(
        'git', 'merge-base', start, finish, ignore_err=True)
    if merge_base != start:
        raise ValueError(
            'git merge base is not the start commit in range',
            merge_base, start, finish)


def _get_merge_base_from_github(slug, start, finish):
    """Retrieves the merge base of two commits from the GitHub API.

    This is intended to be used in cases where one of the commits
    is no longer in the local checkout, but is still around on GitHub.

    :type slug: str
    :param slug: The GitHub repo slug for the current build.
                 Of the form ``{organization}/{repository}``.

    :type start: str
    :param start: The start commit in a range.

    :type finish: str
    :param finish: The last commit in a range.

    :rtype: str
    :returns: The commit SHA of the merge base.
    :raises KeyError: If the payload doesn't contain the nested key
                      merge_base_commit->sha.
    """
    payload = _github.commit_compare(slug, start, finish)
    try:
        return payload['merge_base_commit']['sha']
    except KeyError:
        raise KeyError(
            'Missing key in the GitHub API payload',
            'expected merge_base_commit->sha',
            payload, slug, start, finish)


def _push_build_base(slug):
    """Get the diffbase for a Travis "push" build.

    :type slug: str
    :param slug: The GitHub repo slug for the current build.
                 Of the form ``{organization}/{repository}``.

    :rtype: str
    :returns: The commit SHA of the diff base.
    """
    start, finish = _get_commit_range()
    # Resolve the start object name into a 40-char SHA1 hash.
    start_full = _utils.check_output('git', 'rev-parse', start,
                                     ignore_err=True)

    if start_full is None:
        # In this case, the start commit isn't in history so we
        # need to use the GitHub API.
        return _get_merge_base_from_github(slug, start, finish)
    else:
        # In this case, the start commit is in history so we
        # expect it to also be the merge base of the start and finish
        # commits.
        _verify_merge_base(start_full, finish)
        return start_full


def _travis_slug():
    """Get the GitHub repo slug for the current build.

    Of the form ``{organization}/{repository}``.

    :rtype: str
    :returns: The slug for the current build.
    :raises EnvironmentError: if the ``TRAVIS_REPO_SLUG`` environment variable
                              isn't set during a Travis build.
    """
    try:
        return os.environ[env.TRAVIS_SLUG_ENV]
    except KeyError as exc:
        msg = ('Travis build does not have a '
               'repo slug set (via %s)') % (env.TRAVIS_SLUG_ENV,)
        raise EnvironmentError(exc, msg)


# pylint: disable=too-few-public-methods
class TravisEventType(enum.Enum):
    """Enum representing all possible Travis event types."""
    push = 'push'
    pull_request = 'pull_request'
    api = 'api'
    cron = 'cron'
# pylint: enable=too-few-public-methods


class Travis(object):
    """Represent Travis state and cache return values."""

    _active = _UNSET
    _base = _UNSET
    _branch = _UNSET
    _event_type = _UNSET
    _pr = _UNSET
    _slug = _UNSET

    # pylint: disable=missing-returns-doc
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
        :raises NotImplementedError: If not in a "pull request" or
                                     "push" build.
        """
        if self._base is _UNSET:
            if self.in_pr:
                self._base = self.branch
            elif self.event_type is TravisEventType.push:
                self._base = _push_build_base(self.slug)
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
    def event_type(self):
        """Indicates if currently running in Travis.

        :rtype: bool
        """
        if self._event_type is _UNSET:
            self._event_type = _travis_event_type()
        return self._event_type

    @property
    def in_pr(self):
        """Indicates if currently running in Travis pull request.

        This uses the ``TRAVIS_EVENT_TYPE`` environment variable to check
        if currently in a pull request. Though it doesn't use the
        ``TRAVIS_PULL_REQUEST`` environment variable, checking that the
        value is set to an integer would be a perfectly valid approach.

        :rtype: bool
        """
        return self.event_type is TravisEventType.pull_request

    # pylint: disable=invalid-name
    @property
    def pr(self):
        """The current Travis pull request (if any).

        If there is no active pull request, returns :data:`None`.

        :rtype: int
        """
        if self._pr is _UNSET:
            self._pr = _travis_pr()
        return self._pr
    # pylint: enable=invalid-name

    @property
    def slug(self):
        """The current slug in the Travis build.

        Of the form ``{organization}/{repository}``.

        :rtype: str
        """
        if self._slug is _UNSET:
            self._slug = _travis_slug()
        return self._slug
    # pylint: enable=missing-returns-doc


def in_travis():
    """Detect if we are running in Travis.

    See the :class:`Travis` class for a
    more comprehensive way to determine the Travis configuration,
    with caching enabled. In particular, for this method, see
    :attr:`Travis.active`.

    :rtype: bool
    :returns: Flag indicating if we are running on Travis.
    """
    return Travis().active


def in_travis_pr():
    """Detect if we are running in a pull request on Travis.

    See the :class:`Travis` class for a
    more comprehensive way to determine the Travis configuration,
    with caching enabled. In particular, for this method, see
    :attr:`Travis.in_pr`.

    :rtype: bool
    :returns: Flag indicating if we are in a pull request on Travis.
    """
    return Travis().in_pr


def travis_branch():
    """Get the current branch of the PR.

    See the :class:`Travis` class for a
    more comprehensive way to determine the Travis configuration,
    with caching enabled. In particular, for this method, see
    :attr:`Travis.branch`.

    .. note::

        This assumes we already know we are running in Travis
        during a PR.

    :rtype: str
    :returns: The name of the branch the current pull request is
              changed against.
    """
    return Travis().branch
