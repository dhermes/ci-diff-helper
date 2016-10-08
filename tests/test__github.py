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

import unittest


class Test__rate_limit_info(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(response):
        from ci_diff_helper._github import _rate_limit_info
        return _rate_limit_info(response)

    def test_it(self):
        import sys
        import mock
        import requests
        from ci_diff_helper import _github

        response = requests.Response()
        remaining = '17'
        response.headers[_github._RATE_REMAINING_HEADER] = remaining
        rate_limit = '60'
        response.headers[_github._RATE_LIMIT_HEADER] = rate_limit
        rate_reset = '1475953149'
        response.headers[_github._RATE_RESET_HEADER] = rate_reset
        with mock.patch('six.print_') as mocked:
            self._call_function_under_test(response)
            msg = _github._RATE_LIMIT_TEMPLATE % (
                remaining, rate_limit, rate_reset)
            mocked.called_once_with(msg, file=sys.stderr)


class Test_commit_compare(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(slug, start, finish):
        from ci_diff_helper._github import commit_compare
        return commit_compare(slug, start, finish)

    @staticmethod
    def _make_response(status_code, payload):
        import json
        import requests

        response = requests.Response()
        response.status_code = status_code
        response._content = json.dumps(payload).encode('utf-8')
        return response

    def _helper(self, status_code, payload,
                error_class=None, headers=None):
        import mock
        from ci_diff_helper import _github

        if headers is None:
            headers = {}
        response = self._make_response(status_code, payload)

        patch_get = mock.patch('requests.get', return_value=response)
        slug = 'a/b'
        start = '1234'
        finish = '6789'
        expected_url = _github._GH_COMPARE_TEMPLATE % (
            slug, start, finish)
        with patch_get as mocked:
            if error_class is None:
                result = self._call_function_under_test(
                    slug, start, finish)
                self.assertEqual(result, payload)
            else:
                # Patch six.print_ so the test isn't noisy.
                with mock.patch('six.print_'):
                    with self.assertRaises(error_class):
                        self._call_function_under_test(
                            slug, start, finish)
            mocked.assert_called_once_with(expected_url, headers=headers)

    def test_success(self):
        from six.moves import http_client

        payload = {'hi': 'bye'}
        self._helper(http_client.OK, payload)

    def test_success_with_token(self):
        import mock
        from six.moves import http_client
        from ci_diff_helper import environment_vars as env

        payload = {'hi': 'bye'}
        token = 'n00bt0k3nf411'
        mock_env = {env.GH_TOKEN: token}
        headers = {'Authorization': 'token ' + token}
        with mock.patch('os.environ', new=mock_env):
            self._helper(http_client.OK, payload, headers=headers)

    def test_response_failure(self):
        import requests
        from six.moves import http_client

        self._helper(http_client.NOT_FOUND, {},
                     error_class=requests.HTTPError)
