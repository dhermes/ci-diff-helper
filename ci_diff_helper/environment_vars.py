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

"""Comprehensive list of environment variables used in ci-diff-helper.

These environment variables are core this library. They are used to
detect the current environment.

For more details, see the `Travis env docs`_.

.. _Travis env docs: https://docs.travis-ci.com/user/\
                     environment-variables#Default-Environment-Variables
"""

IN_TRAVIS_ENV = 'TRAVIS'
"""Indicates if running in Travis."""

TRAVIS_PR_ENV = 'TRAVIS_PULL_REQUEST'
"""Indicates which Travis pull request we are in.

Is an integer when in a pull request or "false" when not.
"""

TRAVIS_BRANCH_ENV = 'TRAVIS_BRANCH'
"""Indicates the active Travis branch.

In a "push" build, this is the branch that was pushed while
in a "pull request" build it is the branch that a pull
request is against.
"""

TRAVIS_EVENT_TYPE_ENV = 'TRAVIS_EVENT_TYPE'
"""Indicates the type of build that is occurring."""

TRAVIS_RANGE_ENV = 'TRAVIS_COMMIT_RANGE'
"""The range of commits changed in the current build.

This is not particularly useful in a PR build.
"""

TRAVIS_SLUG_ENV = 'TRAVIS_REPO_SLUG'
"""The GitHub repository slug for the current Travis build.

A slug is of the form ``{organization}/{repository}``.
"""

GH_TOKEN = 'GITHUB_OAUTH_TOKEN'
"""GitHub OAuth 2.0 token.

This environment variable must be used to authenticate to
the GitHub API. Making unauthenticated requests on a Continuous
Integration server will typically be `rate limited`_.

.. _rate limited: https://developer.github.com/v3/#rate-limiting
"""
