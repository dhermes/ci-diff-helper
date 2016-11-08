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

"""Set of utilities for dealing with AppVeyor CI.

This module uses a selection of environment variables to detect
the state of AppVeyor configuration. See
:mod:`~ci_diff_helper.environment_vars` for more details.

This module provides a long-lived configuration object
(:class:`AppVeyor`) that caches the returned values and uses
them to compute other useful values.

.. testsetup:: config-obj

  import os
  os.environ = {
      'APPVEYOR': 'True',
      'APPVEYOR_REPO_BRANCH': 'master',
      'APPVEYOR_REPO_PROVIDER': 'github',
  }
  import ci_diff_helper

.. doctest:: config-obj

  >>> config = ci_diff_helper.AppVeyor()
  >>> config.active
  True
  >>> config.branch
  'master'
  >>> config.provider
  <AppVeyorRepoProvider.github: 'github'>
  >>> config.tag is None
  True

It can also be used to detect if a merge commit is
currently being built:

.. testsetup:: merged-commit

  import ci_diff_helper
  config = ci_diff_helper.AppVeyor()
  config._is_merge = True

.. doctest:: merged-commit

  >>> config.is_merge
  True
"""

import os

import enum

from ci_diff_helper import _config_base
from ci_diff_helper import _utils
from ci_diff_helper import environment_vars as env


def _appveyor_provider():
    """Get the code hosting provider for the current AppVeyor build.

    Returns:
        AppVeyorRepoProvider: The code hosting provider for the
            current AppVeyor build.

    Raises:
        ValueError: If the ``APPVEYOR_REPO_PROVIDER`` environment
            variable is not one of the expected values.
    """
    repo_provider = os.getenv(env.APPVEYOR_REPO_ENV, '')
    try:
        return AppVeyorRepoProvider(repo_provider)
    except ValueError:
        raise ValueError('Invalid repo provider', repo_provider,
                         'Expected one of',
                         [enum_val.name for enum_val in AppVeyorRepoProvider])


# pylint: disable=too-few-public-methods
class AppVeyorRepoProvider(enum.Enum):
    """Enum representing all possible AppVeyor repo providers."""
    github = 'github'
    bitbucket = 'bitbucket'
    kiln = 'kiln'
    vso = 'vso'
    gitlab = 'gitlab'
# pylint: enable=too-few-public-methods


class AppVeyor(_config_base.Config):
    """Represent AppVeyor state and cache return values."""

    # Default instance attributes.
    _provider = _utils.UNSET
    # Class attributes.
    _active_env_var = env.IN_APPVEYOR_ENV
    _branch_env_var = env.APPVEYOR_BRANCH_ENV
    _tag_env_var = env.APPVEYOR_TAG_ENV

    # pylint: disable=missing-returns-doc
    @property
    def provider(self):
        """str: The code hosting provider for the current AppVeyor build."""
        if self._provider is _utils.UNSET:
            self._provider = _appveyor_provider()
        return self._provider

    @property
    def tag(self):
        """str: The ``git`` tag of the current AppVeyor build.

        .. note::

            We only expect the ``APPVEYOR_REPO_TAG_NAME`` environment variable
            to be set when ``APPVEYOR_REPO_TAG=true`` indicates the build was
            started by a pushed tag. However, we don't verify that we are in
            a build started by a tag before checking for the tag.
        """
        return super(AppVeyor, self).tag
    # pylint: enable=missing-returns-doc
