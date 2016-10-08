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

.. note::

    When configuring your CI environment, it may be useful to set
    the ``GITHUB_OAUTH_TOKEN`` environment variable
    (:data:`~.environment_vars.GH_TOKEN`). By authenticating in
    GitHub API requests, `rate limiting`_ can be avoided. Unauthenticated
    requests will be subject to rate limiting across the entire
    CI system.

.. _rate limiting: https://developer.github.com/v3/#rate-limiting
"""

from ci_diff_helper.git_tools import get_checked_in_files
from ci_diff_helper.git_tools import git_root
from ci_diff_helper.travis import in_travis
from ci_diff_helper.travis import in_travis_pr
from ci_diff_helper.travis import travis_branch
