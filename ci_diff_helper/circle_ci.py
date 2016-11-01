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

The commands in this module are ``git`` centric.

This module uses a selection of environment variables to detect
the state of Circle CI configuration. See
:mod:`~ci_diff_helper.environment_vars` for more details.

This module provides a long-lived configuration object
(:class:`CircleCI`) that caches the returned values and uses
them to compute other useful values.

.. testsetup:: config-obj

  import os
  os.environ = {
      'CIRCLECI': 'true',
      'CIRCLE_BRANCH': 'master',
      'CIRCLE_TAG': '0.4.2',
  }
  import ci_diff_helper

.. doctest:: config-obj

  >>> config = ci_diff_helper.CircleCI()
  >>> config.active
  True
  >>> config.branch
  'master'
  >>> config.tag
  '0.4.2'

It can also be used to detect if a merge commit is
currently being built:

.. testsetup:: merged-commit

  import ci_diff_helper
  config = ci_diff_helper.CircleCI()
  config._is_merge = True

.. doctest:: merged-commit

  >>> config.is_merge
  True
"""

from ci_diff_helper import _config_base
from ci_diff_helper import environment_vars as env


class CircleCI(_config_base.Config):
    """Represent CircleCI state and cache return values."""

    # Class attributes.
    _active_env_var = env.IN_CIRCLE_CI_ENV
    _branch_env_var = env.CIRCLE_CI_BRANCH_ENV
    _tag_env_var = env.CIRCLE_CI_TAG_ENV
