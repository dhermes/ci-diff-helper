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

For an open source project, running unit tests, system tests, torture tests,
fuzz tests, integration tests, code quality checks, etc. can quickly become
a large task.

In order to limit the amount of time and resources that these jobs require,
this tool provides a way to determine which files have changed and provides
a Python API for these changes. In addition, this library provides the
corresponding commit SHA (or other artifact) that is used as the diffbase.

The library supports (planned)

* Continuous Integration Services

  * `Travis CI`_
  * `AppVeyor`_
  * `CircleCI`_

* Verson Control Systems

  * `git`_

* Project Hosting Sites

  * `GitHub`_

.. _Travis CI: https://travis-ci.com/
.. _AppVeyor: https://www.appveyor.com/
.. _CircleCI: https://circleci.com/
.. _git: https://git-scm.com/
.. _GitHub: https://github.com/

.. note::

    When configuring your CI environment, it may be useful to set
    the ``GITHUB_OAUTH_TOKEN`` environment variable
    (:data:`~.environment_vars.GH_TOKEN`). By authenticating in
    GitHub API requests, `rate limiting`_ can be avoided. Unauthenticated
    requests will be subject to rate limiting across the entire
    CI system.

.. _rate limiting: https://developer.github.com/v3/#rate-limiting

To use this in your project, first install:

.. code-block:: bash

  $ pip install --upgrade ci-diff-helper

Once you've done that, you can automatically detect your
current environment and get a configuration object with
information about your environment:

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

Common Configuration Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Long-lived configuration objects are provided as an interface for
CI system information. These config objects cache the returned values
for each property and use them to compute other useful values.

Each such configuration type (e.g. :class:`~.appveyor.AppVeyor`,
:class:`~.circle_ci.CircleCI`, :class:`~.travis.Travis`) has a
common set of properties.

.. testsetup:: shared

  import os
  import ci_diff_helper
  os.environ = {
      'CIRCLECI': 'true',
      'CIRCLE_BRANCH': 'pull/808',
  }
  config = ci_diff_helper.CircleCI()
  config._is_merge = False

.. doctest:: shared

  >>> config
  <CircleCI (active=True)>
  >>> config.active
  True
  >>> config.branch
  'pull/808'
  >>> config.tag is None
  True

All configuration types can also be used to detect if a merge
commit is currently being built:

.. doctest:: shared

  >>> config.is_merge
  False

``git`` tools
~~~~~~~~~~~~~

The helpers :func:`~git_tools.git_root` and
:func:`~git_tools.get_checked_in_files` are provided as
tools for a ``git``-based project. Being able to get the
root of the current ``git`` checkout may be needed to collect
files, execute scripts, etc. Getting all checked in files can
be useful for things like test collection, file linting, etc.

.. testsetup:: git

  import ci_diff_helper
  from ci_diff_helper import _utils

  root_dir = '/path/to/your/git_checkout'
  calls = [
      ('git', 'rev-parse', '--show-toplevel'),
      ('git', 'rev-parse', '--show-toplevel'),
      ('git', 'ls-files', root_dir),
  ]
  files = (
      '/path/to/your/git_checkout/setup.py\\n'
      '/path/to/your/git_checkout/project/__init__.py\\n'
      '/path/to/your/git_checkout/project/feature.py')
  results = [
      root_dir,
      root_dir,
      files,
  ]

  def mock_check(*args):
      assert args == calls.pop(0)
      return results.pop(0)

  _utils.check_output = mock_check

.. doctest:: git
  :options: +NORMALIZE_WHITESPACE

  >>> ci_diff_helper.git_root()
  '/path/to/your/git_checkout'
  >>> ci_diff_helper.get_checked_in_files()
  ['/path/to/your/git_checkout/setup.py',
   '/path/to/your/git_checkout/project/__init__.py',
   '/path/to/your/git_checkout/project/feature.py']
"""

from ci_diff_helper.appveyor import AppVeyor
from ci_diff_helper.circle_ci import CircleCI
from ci_diff_helper.git_tools import get_checked_in_files
from ci_diff_helper.git_tools import git_root
from ci_diff_helper.travis import Travis


__all__ = [
    'AppVeyor',
    'CircleCI',
    'get_checked_in_files',
    'get_config',
    'git_root',
    'Travis',
]


def get_config():
    """Get configuration for the current environment.

    Returns:
        Union[~appveyor.AppVeyor, ~circle_ci.CircleCI, ~travis.Travis]: A
        configuration class for the current environment.

    Raises:
        OSError: If no (unique) environment is active.
    """
    choices = [AppVeyor(), CircleCI(), Travis()]
    current = []
    for choice in choices:
        if choice.active:
            current.append(choice)

    if len(current) != 1:
        raise OSError(
            None, 'Could not find unique environment. Found:',
            current)
    return current[0]
