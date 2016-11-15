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


class Test__circle_ci_pr(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import circle_ci
        return circle_ci._circle_ci_pr()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        valid_int = '331'
        actual_val = 331
        self.assertEqual(int(valid_int), actual_val)
        mock_env = {env.CIRCLE_CI_PR_NUM: valid_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertEqual(self._call_function_under_test(), actual_val)

    def test_failure_unset(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertIsNone(self._call_function_under_test())

    def test_failure_bad_value(self):
        import mock
        from ci_diff_helper import environment_vars as env

        not_int = 'not-int'
        self.assertRaises(ValueError, int, not_int)
        mock_env = {env.CIRCLE_CI_PR_NUM: not_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertIsNone(self._call_function_under_test())


class Test__circle_ci_repo_url(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import circle_ci
        return circle_ci._circle_ci_repo_url()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        repo_url = 'https://github.com/foo/bar'
        mock_env = {env.CIRCLE_CI_REPO_URL: repo_url}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertEqual(result, repo_url)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(OSError):
                self._call_function_under_test()


class TestCircleCI(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import circle_ci
        return circle_ci.CircleCI

    def _make_one(self):
        klass = self._get_target_class()
        return klass()

    def test_constructor(self):
        from ci_diff_helper import _utils

        klass = self._get_target_class()
        config = self._make_one()
        self.assertIsInstance(config, klass)
        self.assertIs(config._active, _utils.UNSET)
        self.assertIs(config._branch, _utils.UNSET)
        self.assertIs(config._is_merge, _utils.UNSET)
        self.assertIs(config._tag, _utils.UNSET)

    def test___repr__(self):
        import mock

        config = self._make_one()
        with mock.patch('os.environ', new={}):
            self.assertEqual(repr(config), '<CircleCI (active=False)>')

    def _pr_helper(self, pr_val):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        # Make sure there is no _pr value set.
        self.assertIs(config._pr, _utils.UNSET)

        # Patch the helper so we can control the value.
        travis_pr_patch = mock.patch(
            'ci_diff_helper.circle_ci._circle_ci_pr', return_value=pr_val)
        with travis_pr_patch as mocked:
            result = config.pr
            self.assertIs(result, pr_val)
            mocked.assert_called_once_with()

        return config

    def test_pr_property(self):
        pr_val = 1337
        self._pr_helper(pr_val)

    def test_pr_property_cache(self):
        pr_val = 42043
        config = self._pr_helper(pr_val)
        # Test that the value is cached.
        self.assertIs(config._pr, pr_val)
        # Test that cached value is re-used.
        self.assertIs(config.pr, pr_val)

    def test_in_pr_property(self):
        config = self._make_one()
        # Patch with an actual PR.
        config._pr = 1337
        self.assertTrue(config.in_pr)

    def test_in_pr_property_fails(self):
        config = self._make_one()
        # Patch a missing PR.
        config._pr = None
        self.assertFalse(config.in_pr)

    def _repo_url_helper(self, repo_url_val):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        # Make sure there is no _repo_url value set.
        self.assertIs(config._repo_url, _utils.UNSET)

        # Patch the helper so we can control the value.
        repo_url_patch = mock.patch(
            'ci_diff_helper.circle_ci._circle_ci_repo_url',
            return_value=repo_url_val)
        with repo_url_patch as mocked:
            result = config.repo_url
            self.assertIs(result, repo_url_val)
            mocked.assert_called_once_with()

        return config

    def test_repo_url_property(self):
        repo_url_val = 'reap-oh-no-you-are-elle'
        self._repo_url_helper(repo_url_val)

    def test_repo_url_property_cache(self):
        repo_url_val = 'read-poem-earl'
        config = self._repo_url_helper(repo_url_val)
        # Test that the value is cached.
        self.assertIs(config._repo_url, repo_url_val)
        # Test that cached value is re-used.
        self.assertIs(config.repo_url, repo_url_val)
