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

"""Helper to make calls to the GitHub API."""

import os
import sys

import requests
import six
from six.moves import http_client

from ci_diff_helper import environment_vars as env


_GH_COMPARE_TEMPLATE = 'https://api.github.com/repos/{}/compare/{}...{}'
_GH_PR_TEMPLATE = 'https://api.github.com/repos/{}/pulls/{:d}'
_RATE_REMAINING_HEADER = 'X-RateLimit-Remaining'
_RATE_LIMIT_HEADER = 'X-RateLimit-Limit'
_RATE_RESET_HEADER = 'X-RateLimit-Reset'
_RATE_LIMIT_TEMPLATE = '{:>25}: {{}}\n{:>25}: {{}}\n{:>25}: {{}}'.format(
    _RATE_REMAINING_HEADER, _RATE_LIMIT_HEADER, _RATE_RESET_HEADER)
_GH_ENV_VAR_MSG = (
    'You can avoid being rate limited by storing a GitHub OAuth '
    'token in the {} environment variable').format(env.GH_TOKEN)


def _rate_limit_info(response):
    """Print response rate limit information to stderr.

    Args:
        response (requests.Response): A GitHub API response.
    """
    remaining = response.headers.get(_RATE_REMAINING_HEADER)
    rate_limit = response.headers.get(_RATE_LIMIT_HEADER)
    rate_reset = response.headers.get(_RATE_RESET_HEADER)
    msg = _RATE_LIMIT_TEMPLATE.format(remaining, rate_limit, rate_reset)
    six.print_(msg, file=sys.stderr)
    six.print_(_GH_ENV_VAR_MSG, file=sys.stderr)


def _get_headers():
    """Get headers for GitHub API request.

    Attempts to add a GitHub token to headers if available.

    Returns:
        dict: The headers for a GitHub API request.
    """
    headers = {}
    github_token = os.getenv(env.GH_TOKEN, None)
    if github_token is not None:
        headers['Authorization'] = 'token ' + github_token

    return headers


def _maybe_fail(response):
    """Fail and print info if an API request was not successful.

    Args:
        response (requests.models.Response): A ``requests`` response
            from a GitHub API request.

    Raises:
        requests.exceptions.HTTPError: If the GitHub API request fails.
    """
    if response.status_code != http_client.OK:
        _rate_limit_info(response)
        response.raise_for_status()


def commit_compare(slug, start, finish):
    """Makes GitHub API request to compare two commits.

    Args:
        slug (str): The GitHub repo slug for the current build.
            Of the form ``{organization}/{repository}``.
        start (str): The start commit in a range.
        finish (str): The last commit in a range.

    Returns:
        dict: The parsed JSON payload of the request.

    Raises:
        requests.exceptions.HTTPError: If the GitHub API request fails.
    """
    api_url = _GH_COMPARE_TEMPLATE.format(slug, start, finish)

    headers = _get_headers()
    response = requests.get(api_url, headers=headers)
    _maybe_fail(response)

    return response.json()


def pr_info(slug, pr_id):
    """Makes GitHub API request to info about a pull request.

    Args:
        slug (str): The GitHub repo slug for the current build.
            Of the form ``{organization}/{repository}``.
        pr_id (int): The pull request ID.

    Returns:
        dict: The pull request information.

    Raises:
        requests.exceptions.HTTPError: If the GitHub API request fails.
    """
    api_url = _GH_PR_TEMPLATE.format(slug, pr_id)

    headers = _get_headers()
    response = requests.get(api_url, headers=headers)
    _maybe_fail(response)

    return response.json()
