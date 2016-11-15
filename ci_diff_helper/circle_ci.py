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

During a pull request build, we can determine information about
the current PR being built:

.. testsetup:: circle-ci-pr

  import os
  os.environ = {
      'CIRCLECI': 'true',
      'CIRCLE_PR_NUMBER': '23',
      'CIRCLE_BRANCH': 'pull/23',
  }
  import ci_diff_helper

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
"""

import os

from ci_diff_helper import _config_base
from ci_diff_helper import _utils
from ci_diff_helper import environment_vars as env


_REPO_URL_TEMPLATE = (
    'CircleCI build does not have a repo URL set (via {})')


def _circle_ci_pr():
    """Get the current CircleCI pull request (if any).

    Returns:
        Optional[int]: The current pull request ID.
    """
    try:
        return int(os.getenv(env.CIRCLE_CI_PR_NUM, ''))
    except ValueError:
        return None


def _circle_ci_repo_url():
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


class CircleCI(_config_base.Config):
    """Represent CircleCI state and cache return values."""

    # Default instance attributes.
    _pr = _utils.UNSET
    _repo_url = _utils.UNSET
    # Class attributes.
    _active_env_var = env.IN_CIRCLE_CI
    _branch_env_var = env.CIRCLE_CI_BRANCH
    _tag_env_var = env.CIRCLE_CI_TAG

    # pylint: disable=invalid-name
    @property
    def pr(self):
        """int: The current CircleCI pull request (if any).

        If there is no active pull request, returns :data:`None`.
        """
        if self._pr is _utils.UNSET:
            self._pr = _circle_ci_pr()
        return self._pr
    # pylint: enable=invalid-name

    @property
    def in_pr(self):
        """bool: Indicates if currently running in CircleCI pull request.

        This uses the ``CIRCLE_PR_NUMBER`` environment variable to check
        if currently in a pull request.
        """
        return self.pr is not None

    @property
    def repo_url(self):
        """str: The URL of the current repository being built.

        For example: ``https://github.com/{organization}/{repository}`` or
        ``https://bitbucket.org/{user}/{repository}``.
        """
        if self._repo_url is _utils.UNSET:
            self._repo_url = _circle_ci_repo_url()
        return self._repo_url
