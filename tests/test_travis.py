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


class Test__in_travis(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _in_travis
        return _in_travis()

    def test_success(self):
        import mock
        from ci_diff_helper import travis

        mock_env = {travis._IN_TRAVIS_ENV: 'true'}
        with mock.patch('os.environ', new=mock_env):
            self.assertTrue(self._call_function_under_test())

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertFalse(self._call_function_under_test())


class Test__travis_pr(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _travis_pr
        return _travis_pr()

    def test_success(self):
        import mock
        from ci_diff_helper import travis

        valid_int = '1234'
        actual_val = 1234
        self.assertEqual(int(valid_int), actual_val)
        mock_env = {travis._TRAVIS_PR_ENV: valid_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertEqual(self._call_function_under_test(), actual_val)

    def test_failure_unset(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertIsNone(self._call_function_under_test())

    def test_failure_bad_value(self):
        import mock
        from ci_diff_helper import travis

        not_int = 'not-int'
        self.assertRaises(ValueError, int, not_int)
        mock_env = {travis._TRAVIS_PR_ENV: not_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertIsNone(self._call_function_under_test())


class Test__travis_branch(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _travis_branch
        return _travis_branch()

    def test_success(self):
        import mock
        from ci_diff_helper import travis

        branch = 'this-very-branch'
        mock_env = {travis._TRAVIS_BRANCH_ENV: branch}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertEqual(result, branch)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(OSError):
                self._call_function_under_test()


class TestTravis(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import travis
        return travis.Travis

    def _make_one(self):
        klass = self._get_target_class()
        return klass()

    def test_constructor(self):
        from ci_diff_helper import travis

        klass = self._get_target_class()
        config = self._make_one()
        self.assertIsInstance(config, klass)
        self.assertIs(config._active, travis._UNSET)
        self.assertIs(config._pr, travis._UNSET)

    def _active_helper(self, active_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _active value set.
        self.assertIs(config._active, travis._UNSET)

        # Patch the helper so we can control the value.
        in_travis_patch = mock.patch(
            'ci_diff_helper.travis._in_travis', return_value=active_val)
        with in_travis_patch as mocked:
            result = config.active
            self.assertIs(result, active_val)
            mocked.assert_called_once_with()

        return config

    def test_active_property(self):
        active_val = object()
        self._active_helper(active_val)

    def test_active_property_cache(self):
        active_val = object()
        config = self._active_helper(active_val)
        # Test that the value is cached.
        self.assertIs(config._active, active_val)
        # Test that cached value is re-used.
        self.assertIs(config.active, active_val)

    def _pr_helper(self, pr_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _pr value set.
        self.assertIs(config._pr, travis._UNSET)

        # Patch the helper so we can control the value.
        travis_pr_patch = mock.patch(
            'ci_diff_helper.travis._travis_pr', return_value=pr_val)
        with travis_pr_patch as mocked:
            result = config.pr
            self.assertIs(result, pr_val)
            mocked.assert_called_once_with()

        return config

    def test_pr_property(self):
        pr_val = 1337
        self._pr_helper(pr_val)

    def test_pr_property_cache(self):
        pr_val = 42
        config = self._pr_helper(pr_val)
        # Test that the value is cached.
        self.assertIs(config._pr, pr_val)
        # Test that cached value is re-used.
        self.assertIs(config.pr, pr_val)

    def _branch_helper(self, branch_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _branch value set.
        self.assertIs(config._branch, travis._UNSET)

        # Patch the helper so we can control the value.
        in_travis_patch = mock.patch(
            'ci_diff_helper.travis._travis_branch',
            return_value=branch_val)
        with in_travis_patch as mocked:
            result = config.branch
            self.assertIs(result, branch_val)
            mocked.assert_called_once_with()

        return config

    def test_branch_property(self):
        branch_val = 'branch-on-a-tree-in-a-forest'
        self._branch_helper(branch_val)

    def test_branch_property_cache(self):
        branch_val = 'make-tomorrow-a-tree'
        config = self._branch_helper(branch_val)
        # Test that the value is cached.
        self.assertIs(config._branch, branch_val)
        # Test that cached value is re-used.
        self.assertIs(config.branch, branch_val)

    def test_branch_property_error(self):
        import mock

        config = self._make_one()
        with mock.patch('os.environ', new={}):
            with self.assertRaises(OSError):
                config.branch
