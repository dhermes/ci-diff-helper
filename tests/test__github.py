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
        from ci_diff_helper import _github
        return _github._rate_limit_info(response)

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
            msg = _github._RATE_LIMIT_TEMPLATE.format(
                remaining, rate_limit, rate_reset)
            self.assertEqual(mocked.call_count, 2)
            mocked.assert_any_call(msg, file=sys.stderr)
            mocked.assert_any_call(_github._GH_ENV_VAR_MSG,
                                   file=sys.stderr)


class Test__get_headers(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import _github
        return _github._get_headers()

    def test_without_auth(self):
        import mock

        with mock.patch('os.environ', new={}):
            headers = self._call_function_under_test()

        self.assertEqual(headers, {})

    def test_with_auth(self):
        import mock
        from ci_diff_helper import environment_vars as env

        token = 'n00bt0k3nf411'
        mock_env = {env.GH_TOKEN: token}
        with mock.patch('os.environ', new=mock_env):
            headers = self._call_function_under_test()

        expected = {'Authorization': 'token ' + token}
        self.assertEqual(headers, expected)


class Test__maybe_fail(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(response):
        from ci_diff_helper import _github
        return _github._maybe_fail(response)

    def test_success(self):
        import mock
        import requests
        from six.moves import http_client

        response = mock.Mock(spec=requests.Response,
                             status_code=http_client.OK)
        self._call_function_under_test(response)

        response.raise_for_status.assert_not_called()

    def test_failure(self):
        import mock
        import requests
        from six.moves import http_client

        response = requests.Response()
        response.status_code = http_client.FORBIDDEN

        to_patch = 'ci_diff_helper._github._rate_limit_info'
        with mock.patch(to_patch) as patched:
            with self.assertRaises(requests.HTTPError):
                self._call_function_under_test(response)
            patched.assert_called_once_with(response)


class Test_commit_compare(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(slug, start, finish):
        from ci_diff_helper import _github
        return _github.commit_compare(slug, start, finish)

    @staticmethod
    def _make_response(payload):
        import json
        import requests
        from six.moves import http_client

        response = requests.Response()
        response.status_code = http_client.OK
        response._content = json.dumps(payload).encode('utf-8')
        return response

    def test_success(self):
        import mock

        from ci_diff_helper import _github

        payload = {'hi': 'bye'}
        response = self._make_response(payload)

        patch_get = mock.patch('requests.get', return_value=response)
        slug = 'a/b'
        start = '1234'
        finish = '6789'
        expected_url = _github._GH_COMPARE_TEMPLATE.format(
            slug, start, finish)

        headers_mock = mock.Mock(
            return_value=mock.sentinel.headers)
        fail_mock = mock.Mock()
        with mock.patch.multiple('ci_diff_helper._github',
                                 _get_headers=headers_mock,
                                 _maybe_fail=fail_mock):
            with patch_get as mocked_get:
                result = self._call_function_under_test(
                    slug, start, finish)

        self.assertEqual(result, payload)

        # Verify mocks.
        headers_mock.assert_called_once_with()
        fail_mock.assert_called_once_with(response)
        mocked_get.assert_called_once_with(
            expected_url, headers=mock.sentinel.headers)


class Test_pr_info(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(slug, pr_id):
        from ci_diff_helper import _github
        return _github.pr_info(slug, pr_id)

    @staticmethod
    def _make_response(payload):
        import json
        import requests
        from six.moves import http_client

        response = requests.Response()
        response.status_code = http_client.OK
        response._content = json.dumps(payload).encode('utf-8')
        return response

    def test_success(self):
        import mock

        from ci_diff_helper import _github

        base_sha = '04facb05d80e871107892b3635e24fee60a4fc36'
        payload = {'base': {'sha': base_sha}}
        response = self._make_response(payload)

        patch_get = mock.patch('requests.get', return_value=response)
        slug = 'a/b'
        pr_id = 808
        expected_url = _github._GH_PR_TEMPLATE.format(slug, pr_id)

        headers_mock = mock.Mock(
            return_value=mock.sentinel.headers)
        fail_mock = mock.Mock()
        with mock.patch.multiple('ci_diff_helper._github',
                                 _get_headers=headers_mock,
                                 _maybe_fail=fail_mock):
            with patch_get as mocked_get:
                result = self._call_function_under_test(
                    slug, pr_id)

        self.assertEqual(result, payload)

        # Verify mocks.
        headers_mock.assert_called_once_with()
        fail_mock.assert_called_once_with(response)
        mocked_get.assert_called_once_with(
            expected_url, headers=mock.sentinel.headers)
