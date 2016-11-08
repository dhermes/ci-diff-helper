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
from ci_diff_helper import _config_base
from ci_diff_helper import _utils
from ci_diff_helper import environment_vars as env
from ci_diff_helper import git_tools


_RANGE_DELIMITER = '...'
_SLUG_TEMPLATE = (
    'Travis build does not have a repo slug set (via {})')


def _travis_pr():
    """Get the current Travis pull request (if any).

    Returns:
        int: The current pull request ID.
    """
    try:
        return int(os.getenv(env.TRAVIS_PR_ENV, ''))
    except ValueError:
        return None


def _travis_event_type():
    """Get the event type of the current Travis build

    Returns:
        TravisEventType: The type of the current Travis build.

    Raises:
        ValueError: If the ``TRAVIS_EVENT_TYPE`` environment
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

    .. note::

        This will throw an :exc:`OSError` on the very first "push" build
        for a branch. This is because Travis leaves the value empty in
        builds triggered by the initial commit of a new branch.

    Returns:
        Tuple[str, str]: The ``start``, ``finish`` pair from the commit range.

    Raises:
        OSError: If the ``TRAVIS_COMMIT_RANGE`` does not contain
            '...' (which indicates a start and end commit).
    """
    commit_range = os.getenv(env.TRAVIS_RANGE_ENV, '')
    try:
        start, finish = commit_range.split(_RANGE_DELIMITER)
        return start, finish
    except ValueError as exc:
        raise OSError(
            exc, 'Commit range in unexpected format', commit_range)


def _verify_merge_base(start, finish):
    """Verifies that the merge base of a commit range **is** the start.

    Args:
        start (str): The start commit in a range.
        finish (str): The last commit in a range.

    Raises:
        ValueError: If the merge base is not the start commit.
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

    Args:
        slug (str): The GitHub repo slug for the current build.
            Of the form ``{organization}/{repository}``.
        start (str): The start commit in a range.
        finish (str): The last commit in a range.

    Returns:
        str: The commit SHA of the merge base.

    Raises:
        KeyError: If the payload doesn't contain the nested key
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

    Args:
        slug (str): The GitHub repo slug for the current build.
            Of the form ``{organization}/{repository}``.

    Returns:
        str: The commit SHA of the diff base.
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

    Returns:
        str: The slug for the current build.

    Raises:
        OSError: If the ``TRAVIS_REPO_SLUG`` environment variable
            isn't set during a Travis build.
    """
    try:
        return os.environ[env.TRAVIS_SLUG_ENV]
    except KeyError as exc:
        msg = _SLUG_TEMPLATE.format(env.TRAVIS_SLUG_ENV)
        raise OSError(exc, msg)


# pylint: disable=too-few-public-methods
class TravisEventType(enum.Enum):
    """Enum representing all possible Travis event types."""
    push = 'push'
    pull_request = 'pull_request'
    api = 'api'
    cron = 'cron'
# pylint: enable=too-few-public-methods


class Travis(_config_base.Config):
    """Represent Travis state and cache return values."""

    # Default instance attributes.
    _base = _utils.UNSET
    _event_type = _utils.UNSET
    _merged_pr = _utils.UNSET
    _pr = _utils.UNSET
    _slug = _utils.UNSET
    # Class attributes.
    _active_env_var = env.IN_TRAVIS_ENV
    _branch_env_var = env.TRAVIS_BRANCH_ENV
    _tag_env_var = env.TRAVIS_TAG_ENV

    # pylint: disable=missing-returns-doc
    @property
    def base(self):
        """str: The ``git`` object that current build is changed against.

        The ``git`` object can be any of a branch name, tag, a commit SHA
        or a special reference.

        .. note::

            This will throw an :exc:`OSError` on the very first "push" build
            for a branch. This is because Travis leaves the value empty in
            builds triggered by the initial commit of a new branch.

        Raises:
            NotImplementedError: If not in a "pull request" or
                "push" build.
        """
        if self._base is _utils.UNSET:
            if self.in_pr:
                self._base = self.branch
            elif self.event_type is TravisEventType.push:
                self._base = _push_build_base(self.slug)
            else:
                raise NotImplementedError
        return self._base

    @property
    def event_type(self):
        """bool: Indicates if currently running in Travis."""
        if self._event_type is _utils.UNSET:
            self._event_type = _travis_event_type()
        return self._event_type

    @property
    def in_pr(self):
        """bool: Indicates if currently running in Travis pull request.

        This uses the ``TRAVIS_EVENT_TYPE`` environment variable to check
        if currently in a pull request. Though it doesn't use the
        ``TRAVIS_PULL_REQUEST`` environment variable, checking that the
        value is set to an integer would be a perfectly valid approach.
        """
        return self.event_type is TravisEventType.pull_request

    @property
    def merged_pr(self):
        """int: The pull request corresponding to a merge commit at HEAD.

        If not currently in a push build, returns :data:`None`. If
        the HEAD commit is not a merge commit, returns :data:`None`.

        .. note::

            This only uses the ``git`` checkout to determine the pull
            request ID. A more comprehensive check would involve
            veriying the ID by using the GitHub API.

        Raises:
            NotImplementedError: If not in a "pull request" or
                "push" build.
        """
        if self._merged_pr is not _utils.UNSET:
            return self._merged_pr

        if self.in_pr:
            self._merged_pr = None
        elif self.event_type is TravisEventType.push:
            if git_tools.merge_commit():
                merge_subject = git_tools.commit_subject()
                self._merged_pr = _utils.pr_from_commit(merge_subject)
            else:
                self._merged_pr = None
        else:
            raise NotImplementedError
        return self._merged_pr

    # pylint: disable=invalid-name
    @property
    def pr(self):
        """int: The current Travis pull request (if any).

        If there is no active pull request, returns :data:`None`.
        """
        if self._pr is _utils.UNSET:
            self._pr = _travis_pr()
        return self._pr
    # pylint: enable=invalid-name

    @property
    def slug(self):
        """str: The current slug in the Travis build.

        Of the form ``{organization}/{repository}``.
        """
        if self._slug is _utils.UNSET:
            self._slug = _travis_slug()
        return self._slug

    @property
    def tag(self):
        """str: The ``git`` tag of the current Travis build.

        .. note::

            We only expect the ``TRAVIS_TAG`` environment variable
            to be set during a tag "push" build, but we don't verify
            that we are in a push build before checking for the tag.
        """
        return super(Travis, self).tag
    # pylint: enable=missing-returns-doc


def in_travis():
    """Detect if we are running in Travis.

    See the :class:`Travis` class for a
    more comprehensive way to determine the Travis configuration,
    with caching enabled. In particular, for this method, see
    :attr:`Travis.active`.

    Returns:
        bool: Flag indicating if we are running on Travis.
    """
    return Travis().active


def in_travis_pr():
    """Detect if we are running in a pull request on Travis.

    See the :class:`Travis` class for a
    more comprehensive way to determine the Travis configuration,
    with caching enabled. In particular, for this method, see
    :attr:`Travis.in_pr`.

    Returns:
        bool: Flag indicating if we are in a pull request on Travis.
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

    Returns:
        str: The name of the branch the current pull request is
        changed against.
    """
    return Travis().branch
