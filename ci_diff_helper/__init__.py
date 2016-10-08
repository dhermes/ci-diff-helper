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
(:meth:`~travis.in_travis`, :meth:`~travis.in_travis_pr` and
:meth:`~travis.travis_branch`) to get information about your
current environment.

.. code-block:: python

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

.. code-block:: python

  >>> import ci_diff_helper
  >>> config = ci_diff_helper.Travis()
  >>> config.active
  True
  >>> config.in_pr
  True
  >>> config.branch
  'master'

In addition this configuration provides extra features for
determining a diffbase.

.. code-block:: python

  >>> import ci_diff_helper
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

.. code-block:: python

  >>> import ci_diff_helper
  >>> config = ci_diff_helper.Travis()
  >>> config.event_type
  <TravisEventType.push: 'push'>
  >>> config.pr is None
  True
  >>> config.base
  '4ad7349dc7223ebc02175a16dc577a013044a538'
"""

from ci_diff_helper.git_tools import get_checked_in_files
from ci_diff_helper.git_tools import git_root
from ci_diff_helper.travis import in_travis
from ci_diff_helper.travis import in_travis_pr
from ci_diff_helper.travis import Travis
from ci_diff_helper.travis import travis_branch
