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

* Verson Control Systems

  * `git`_

* Project Hosting Sites (planned)

  * `GitHub`_

.. _Travis CI: https://travis-ci.com/
.. _AppVeyor: https://www.appveyor.com/
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

To use this in your project first install::

  $ pip install --upgrade ci-diff-helper

Once you've done that, you can use some basic functions
(:func:`~travis.in_travis`, :func:`~travis.in_travis_pr` and
:func:`~travis.travis_branch`) to get information about your
current environment.

.. testsetup:: pr

  import os
  os.environ = {
      'TRAVIS': 'true',
      'TRAVIS_EVENT_TYPE': 'pull_request',
      'TRAVIS_BRANCH': 'master',
      'TRAVIS_REPO_SLUG': 'organization/repository',
      'TRAVIS_PULL_REQUEST': '1234',
  }
  import ci_diff_helper

.. doctest:: pr

  >>> import ci_diff_helper
  >>> ci_diff_helper.in_travis()
  True
  >>> ci_diff_helper.in_travis_pr()
  True
  >>> ci_diff_helper.travis_branch()
  'master'

While these functions are convenient, they are "one-shot", i.e. they
compute the value and return it, but don't cache the computed value.

Instead, a long-lived configuration object (:class:`.Travis`) is provided
with the same functionality, but also caches the returned values and
uses them to compute other useful values.

.. doctest:: pr

  >>> config = ci_diff_helper.Travis()
  >>> config.active
  True
  >>> config.in_pr
  True
  >>> config.branch
  'master'

In addition this configuration provides extra features for
determining a diffbase.

.. doctest:: pr

  >>> config = ci_diff_helper.Travis()
  >>> config.event_type
  <TravisEventType.pull_request: 'pull_request'>
  >>> config.slug
  'organization/repository'
  >>> config.pr
  1234
  >>> config.base
  'master'

Not only is this object valuable during a pull request build,
it can also be used to find relevant information in a
"push" build:

.. testsetup:: push

  import os
  os.environ = {
      'TRAVIS_EVENT_TYPE': 'push',
      'TRAVIS_REPO_SLUG': 'organization/repository',
  }
  import ci_diff_helper
  from ci_diff_helper import travis

  def mock_push_base(slug):
      assert slug == 'organization/repository'
      return '4ad7349dc7223ebc02175a16dc577a013044a538'

  travis._push_build_base = mock_push_base

.. doctest:: push

  >>> config = ci_diff_helper.Travis()
  >>> config.event_type
  <TravisEventType.push: 'push'>
  >>> config.pr is None
  True
  >>> config.base
  '4ad7349dc7223ebc02175a16dc577a013044a538'

Though :attr:`~.Travis.base` property can be useful as a diffbase
of a given commit, it may be inappropriate. In a "push" build,
:attr:`~.Travis.base` will be computed from the ``TRAVIS_COMMIT_RANGE``
environment variable, and this value is not particularly reliable.
Instead, :attr:`~.Travis.merged_pr` provides a way to determine the
PR that was merged:

.. testsetup:: push-merged-pr

  import ci_diff_helper
  config = ci_diff_helper.Travis()
  config._merged_pr = 1355
  config._is_merge = True

.. doctest:: push-merged-pr

  >>> config.is_merge
  True
  >>> config.merged_pr
  1355

In addition :func:`~git_tools.git_root` and
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

from ci_diff_helper.git_tools import get_checked_in_files
from ci_diff_helper.git_tools import git_root
from ci_diff_helper.travis import in_travis
from ci_diff_helper.travis import in_travis_pr
from ci_diff_helper.travis import Travis
from ci_diff_helper.travis import travis_branch
