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
"""

import os

import enum

from ci_diff_helper import _utils
from ci_diff_helper import environment_vars as env


def _in_appveyor():
    """Detect if we are running in AppVeyor.

    :rtype: bool
    :returns: Flag indicating if we are running on AppVeyor.
    """
    return os.getenv(env.IN_APPVEYOR_ENV) == 'true'


def _appveyor_provider():
    """Get the code hosting provider for the current AppVeyor build.

    :rtype: :class:`AppVeyorRepoProvider`
    :returns: The code hosting provider for the current AppVeyor build.
    :raises ValueError: if the ``APPVEYOR_REPO_PROVIDER`` environment
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


class AppVeyor(object):
    """Represent AppVeyor state and cache return values."""

    _active = _utils.UNSET
    _provider = _utils.UNSET

    # pylint: disable=missing-returns-doc
    @property
    def active(self):
        """Indicates if currently running in AppVeyor.

        :rtype: bool
        """
        if self._active is _utils.UNSET:
            self._active = _in_appveyor()
        return self._active

    @property
    def provider(self):
        """The code hosting provider for the current AppVeyor build.

        :rtype: str
        """
        if self._provider is _utils.UNSET:
            self._provider = _appveyor_provider()
        return self._provider
    # pylint: enable=missing-returns-doc
