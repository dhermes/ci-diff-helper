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

import requests
from six.moves import http_client


_GH_COMPARE_TEMPLATE = 'https://api.github.com/repos/%s/compare/%s...%s'


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
    response = requests.get(api_url)
    if response.status_code != http_client.OK:
        response.raise_for_status()

    return response.json()
