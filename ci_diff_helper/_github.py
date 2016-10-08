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


_GH_COMPARE_TEMPLATE = 'https://api.github.com/repos/%s/compare/%s...%s'
_RATE_REMAINING_HEADER = 'X-RateLimit-Remaining'
_RATE_LIMIT_HEADER = 'X-RateLimit-Limit'
_RATE_RESET_HEADER = 'X-RateLimit-Reset'
_RATE_LIMIT_TEMPLATE = '%25s: %%s\n%25s: %%s\n%25s: %%s' % (
    _RATE_REMAINING_HEADER, _RATE_LIMIT_HEADER, _RATE_RESET_HEADER)


def _rate_limit_info(response):
    """Print response rate limit information to stderr.

    :type response: :class:`requests.Response`
    :param response: A GitHub API response.
    """
    remaining = response.headers.get(_RATE_REMAINING_HEADER)
    rate_limit = response.headers.get(_RATE_LIMIT_HEADER)
    rate_reset = response.headers.get(_RATE_RESET_HEADER)
    msg = _RATE_LIMIT_TEMPLATE % (remaining, rate_limit, rate_reset)
    six.print_(msg, file=sys.stderr)


def commit_compare(slug, start, finish):
    """Makes GitHub API request to compare two commits.

    :type slug: str
    :param slug: The GitHub repo slug for the current build.
                 Of the form ``{organization}/{repository}``.

    :type start: str
    :param start: The start commit in a range.

    :type finish: str
    :param finish: The last commit in a range.

    :rtype: dict
    :returns: The parsed JSON payload of the request.
    :raises requests.exceptions.HTTPError:
        If the GitHub API request fails.
    """
    api_url = _GH_COMPARE_TEMPLATE % (slug, start, finish)

    headers = {}
    github_token = os.getenv(env.GH_TOKEN, None)
    if github_token is not None:
        headers['Authorization'] = 'token ' + github_token

    response = requests.get(api_url, headers=headers)
    if response.status_code != http_client.OK:
        _rate_limit_info(response)
        response.raise_for_status()

    return response.json()
