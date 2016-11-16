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

"""Set of utilities for dealing with Circle CI.

This module provides a custom configuration type
:class:`CircleCI` for the `CircleCI`_ CI system.

.. _CircleCI: https://circleci.com/

This module uses a selection of environment variables to detect
the state of Circle CI configuration. See
:mod:`~ci_diff_helper.environment_vars` for more details.

:class:`CircleCI` Configuration Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running in CircleCI, you can automatically detect your
current environment and get the configuration object:

.. testsetup:: auto-detect

  import os
  os.environ = {
      'CIRCLECI': 'true',
  }

.. doctest:: auto-detect

  >>> import ci_diff_helper
  >>> config = ci_diff_helper.get_config()
  >>> config
  <CircleCI (active=True)>

To use the :class:`CircleCI` configuration type directly:

.. testsetup:: circle-ci-push

  import os
  os.environ = {
      'CIRCLECI': 'true',
      'CIRCLE_BRANCH': 'master',
      'CIRCLE_TAG': '0.4.2',
      'CIRCLE_REPOSITORY_URL': (
          'https://github.com/organization/repository'),
  }
  import ci_diff_helper

.. doctest:: circle-ci-push

  >>> config = ci_diff_helper.CircleCI()
  >>> config
  <CircleCI (active=True)>
  >>> config.branch
  'master'
  >>> config.tag
  '0.4.2'
  >>> config.repo_url
  'https://github.com/organization/repository'
  >>> config.provider
  <CircleCIRepoProvider.github: 'github'>
  >>> config.slug
  'organization/repository'

During a pull request build, we can determine information about
the current PR being built:

.. testsetup:: circle-ci-pr

  import os
  os.environ = {
      'CIRCLECI': 'true',
      'CIRCLE_PR_NUMBER': '23',
      'CIRCLE_BRANCH': 'pull/23',
      'CIRCLE_REPOSITORY_URL': (
          'https://github.com/organization/repository'),
  }
  import ci_diff_helper
  from ci_diff_helper import _github

  def mock_pr_info(slug, pr_id):
      assert slug == 'organization/repository'
      assert pr_id == 23
      payload = {
          'base': {
              'sha': '7450ebe1a2133442098faa07f3c2c08b612d75f5',
          },
      }
      return payload

  _github.pr_info = mock_pr_info

.. doctest:: circle-ci-pr

  >>> config = ci_diff_helper.CircleCI()
  >>> config
  <CircleCI (active=True)>
  >>> config.in_pr
  True
  >>> config.pr
  23
  >>> config.branch
  'pull/23'
  >>> config.base
  '7450ebe1a2133442098faa07f3c2c08b612d75f5'
"""

import os

import enum

from ci_diff_helper import _config_base
from ci_diff_helper import _github
from ci_diff_helper import _utils
from ci_diff_helper import environment_vars as env


_REPO_URL_TEMPLATE = (
    'CircleCI build does not have a repo URL set (via {})')
_GITHUB_HOST = 'github.com'
_GITHUB_PREFIX = 'https://{}/'.format(_GITHUB_HOST)
_BITBUCKET_HOST = 'bitbucket.org'
_BITBUCKET_PREFIX = 'https://{}/'.format(_BITBUCKET_HOST)


def _circle_ci_pr():
    """Get the current CircleCI pull request (if any).

    Returns:
        Optional[int]: The current pull request ID.
    """
    try:
        return int(os.getenv(env.CIRCLE_CI_PR_NUM, ''))
    except ValueError:
        return None


def _repo_url():
    """Get the repository URL for the current build.

    Returns:
        str: The repository URL for the current build.

    Raises:
        OSError: If the ``CIRCLE_REPOSITORY_URL`` environment variable
            isn't set during a CircleCI build.
    """
    try:
        return os.environ[env.CIRCLE_CI_REPO_URL]
    except KeyError as exc:
        msg = _REPO_URL_TEMPLATE.format(env.CIRCLE_CI_REPO_URL)
        raise OSError(exc, msg)


def _provider_slug(repo_url):
    """Get the code hosting provider for the current CircleCI build.

    Args:
        repo_url (str): The URL of a code hosting repository.

    Returns:
        Tuple[CircleCIRepoProvider, str]: Pair of the code hosting provider
            for the current CircleCI build and the repository slug.

    Raises:
        ValueError: If ``repo_url`` contains the GitHub host but
            does not start with the corresponding expected prefix.
        ValueError: If ``repo_url`` contains the Bitbucket host but
            does not start with the corresponding expected prefix.
        ValueError: If ``repo_url`` doesn't match either the GitHub
            or Bitbucket hosts.
    """
    if _GITHUB_HOST in repo_url:
        if repo_url.startswith(_GITHUB_PREFIX):
            _, slug = repo_url.split(_GITHUB_PREFIX, 1)
            return CircleCIRepoProvider.github, slug
        else:
            raise ValueError('Repository URL contained host',
                             _GITHUB_HOST,
                             'but did not begin as expected',
                             'expected prefix', _GITHUB_PREFIX)
    elif _BITBUCKET_HOST in repo_url:
        if repo_url.startswith(_BITBUCKET_PREFIX):
            _, slug = repo_url.split(_BITBUCKET_PREFIX, 1)
            return CircleCIRepoProvider.bitbucket, slug
        else:
            raise ValueError('Repository URL contained host',
                             _BITBUCKET_HOST,
                             'but did not begin as expected',
                             'expected prefix', _BITBUCKET_PREFIX)
    else:
        raise ValueError('Invalid repo URL', repo_url,
                         'Expected a URL for one of',
                         [enum_val.name for enum_val in CircleCIRepoProvider])


# pylint: disable=too-few-public-methods
class CircleCIRepoProvider(enum.Enum):
    """Enum representing all possible CircleCI repo providers."""
    github = 'github'
    bitbucket = 'bitbucket'
# pylint: enable=too-few-public-methods


class CircleCI(_config_base.Config):
    """Represent CircleCI state and cache return values."""

    # Default instance attributes.
    _base = _utils.UNSET
    _pr = _utils.UNSET
    _pr_info_cached = _utils.UNSET
    _provider = _utils.UNSET
    _repo_url = _utils.UNSET
    _slug = _utils.UNSET
    # Class attributes.
    _active_env_var = env.IN_CIRCLE_CI
    _branch_env_var = env.CIRCLE_CI_BRANCH
    _tag_env_var = env.CIRCLE_CI_TAG

    @property
    def pr(self):
        """int: The current CircleCI pull request (if any).

        If there is no active pull request, returns :data:`None`.
        """
        if self._pr is _utils.UNSET:
            self._pr = _circle_ci_pr()
        return self._pr

    @property
    def in_pr(self):
        """bool: Indicates if currently running in CircleCI pull request.

        This uses the ``CIRCLE_PR_NUMBER`` environment variable to check
        if currently in a pull request.
        """
        return self.pr is not None

    @property
    def _pr_info(self):
        """dict: The information for the current pull request.

        This information is retrieved from the GitHub API and cached.
        It is non-public, but a ``@property`` is used for the caching.

        .. warning::

            This property is only meant to be used in a pull request
            from a GitHub repository.
        """
        if self._pr_info_cached is not _utils.UNSET:
            return self._pr_info_cached

        current_pr = self.pr
        if current_pr is None:
            self._pr_info_cached = {}
        elif self.provider is CircleCIRepoProvider.github:
            self._pr_info_cached = _github.pr_info(self.slug, current_pr)
        else:
            raise NotImplementedError(
                'GitHub is only supported way to retrieve PR info')

        return self._pr_info_cached

    @property
    def repo_url(self):
        """str: The URL of the current repository being built.

        For example: ``https://github.com/{organization}/{repository}`` or
        ``https://bitbucket.org/{user}/{repository}``.
        """
        if self._repo_url is _utils.UNSET:
            self._repo_url = _repo_url()
        return self._repo_url

    @property
    def provider(self):
        """str: The code hosting provider for the current CircleCI build."""
        if self._provider is _utils.UNSET:
            # NOTE: One **could** check here that _slug isn't already set,
            #       but that would be over-protective, since the only
            #       way it could be set also sets _provider.
            self._provider, self._slug = _provider_slug(self.repo_url)
        return self._provider

    @property
    def slug(self):
        """str: The current slug in the CircleCI build.

        Of the form ``{organization}/{repository}``.
        """
        if self._slug is _utils.UNSET:
            # NOTE: One **could** check here that _provider isn't already set,
            #       but that would be over-protective, since the only
            #       way it could be set also sets _slug.
            self._provider, self._slug = _provider_slug(self.repo_url)
        return self._slug

    @property
    def base(self):
        """str: The ``git`` object that current build is changed against.

        The ``git`` object can be any of a branch name, tag, a commit SHA
        or a special reference.

        .. warning::

            This property will currently only work in a build for a
            pull request from a GitHub repository.
        """
        if self._base is not _utils.UNSET:
            return self._base

        if self.in_pr:
            pr_info = self._pr_info
            try:
                self._base = pr_info['base']['sha']
            except KeyError:
                raise KeyError(
                    'Missing key in the GitHub API payload',
                    'expected base->sha',
                    pr_info, self.slug, self.pr)
        else:
            raise NotImplementedError(
                'Diff base currently only supported in a PR from GitHub')

        return self._base
