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

These environment variables are core to this library. They are used
to detect the current environment.

For more details, see the `Travis env docs`_, `AppVeyor env docs`_
and `_CircleCI env docs`.

.. _Travis env docs: https://docs.travis-ci.com/user/\
                     environment-variables#Default-Environment-Variables
.. _AppVeyor env docs: https://www.appveyor.com/docs/environment-variables/
.. _CircleCI env docs: https://circleci.com/docs/environment-variables/
"""

IN_TRAVIS = 'TRAVIS'
"""Indicates if running in Travis."""

TRAVIS_PR = 'TRAVIS_PULL_REQUEST'
"""Indicates which Travis pull request we are in.

Is an integer when in a pull request or "false" when not.
"""

TRAVIS_BRANCH = 'TRAVIS_BRANCH'
"""Indicates the active Travis branch.

In a "push" build, this is the branch that was pushed while
in a "pull request" build it is the branch that a pull
request is against.
"""

TRAVIS_EVENT_TYPE = 'TRAVIS_EVENT_TYPE'
"""Indicates the type of build that is occurring."""

TRAVIS_RANGE = 'TRAVIS_COMMIT_RANGE'
"""The range of commits changed in the current build.

This is not particularly useful in a PR build.

.. note::

    This is empty for builds triggered by the initial commit of
    a new branch.
"""

TRAVIS_SLUG = 'TRAVIS_REPO_SLUG'
"""The GitHub repository slug for the current Travis build.

A slug is of the form ``{organization}/{repository}``.
"""

TRAVIS_TAG = 'TRAVIS_TAG'
"""The tag of the current Travis build.

We only expect the ``TRAVIS_TAG`` environment variable to be set
during a tag "push" build, but it can be set as the empty string
in non-"push" builds.
"""

GH_TOKEN = 'GITHUB_OAUTH_TOKEN'
"""GitHub OAuth 2.0 token.

This environment variable must be used to authenticate to
the GitHub API. Making unauthenticated requests on a Continuous
Integration server will typically be `rate limited`_.

.. _rate limited: https://developer.github.com/v3/#rate-limiting
"""

IN_APPVEYOR = 'APPVEYOR'
"""Indicates if running in AppVeyor."""

APPVEYOR_REPO = 'APPVEYOR_REPO_PROVIDER'
"""The code hosting provided for the repository being tested in AppVeyor."""

APPVEYOR_BRANCH = 'APPVEYOR_REPO_BRANCH'
"""Indicates the active AppVeyor branch.

In a "pull request" build it is the **base** branch the PR is
merging into, otherwise it is the branch being built.
"""

APPVEYOR_TAG = 'APPVEYOR_REPO_TAG_NAME'
"""The tag of the current AppVeyor build.

This will only be valid when ``APPVEYOR_REPO_TAG``, i.e. when the
build was started by a pushed tag.
"""

IN_CIRCLE_CI = 'CIRCLECI'
"""Indicates if running in CircleCI."""

CIRCLE_CI_BRANCH = 'CIRCLE_BRANCH'
"""Indicates the active ``git`` branch being tested on CircleCI."""

CIRCLE_CI_TAG = 'CIRCLE_TAG'
"""The name of the ``git`` tag being tested

Only set if the build is running for a tag.
"""

CIRCLE_CI_PR = 'CI_PULL_REQUEST'
"""Pull request containing the current change set.

If the current build is part of only one pull request, the URL of that
PR will be populated here. If there was more than one pull request, this
field contain one of the pull request URLs (picked randomly).
"""

CIRCLE_CI_PRS = 'CI_PULL_REQUESTS'
"""Comma-separated list of pull requests current build is a part of."""

CIRCLE_CI_REPO_URL = 'CIRCLE_REPOSITORY_URL'
"""A link to the homepage for the current repository."""

CIRCLE_CI_PR_NUM = 'CIRCLE_PR_NUMBER'
"""The ID of the PR that started the current build.

We only expect this environment variable to be set during a
build that is a part of a pull request from a fork.
"""

CIRCLE_CI_PR_REPO = 'CIRCLE_PR_REPONAME'
"""The name of the forked repository that started the current PR build.

We only expect this environment variable to be set during a
build that is a part of a pull request from a fork.
"""

CIRCLE_CI_PR_OWNER = 'CIRCLE_PR_USERNAME'
"""The owner of the forked repository that started the current PR build.

We only expect this environment variable to be set during a
build that is a part of a pull request from a fork.
"""
