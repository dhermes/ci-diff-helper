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


class Test__in_ci(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(env_var):
        from ci_diff_helper._config_base import _in_ci
        return _in_ci(env_var)

    def test_success(self):
        import mock

        env_var = 'MY_CI'
        mock_env = {env_var: 'true'}
        with mock.patch('os.environ', new=mock_env):
            self.assertTrue(self._call_function_under_test(env_var))

    def test_failure(self):
        import mock

        env_var = 'MY_CI'
        with mock.patch('os.environ', new={}):
            self.assertFalse(self._call_function_under_test(env_var))


class Test__ci_branch(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(env_var):
        from ci_diff_helper._config_base import _ci_branch
        return _ci_branch(env_var)

    def test_success(self):
        import mock

        branch = 'this-very-branch'
        env_var = 'MY_CI'
        mock_env = {env_var: branch}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test(env_var)
            self.assertEqual(result, branch)

    def test_failure(self):
        import mock

        env_var = 'MY_CI'
        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                self._call_function_under_test(env_var)


class TestConfig(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import _config_base
        return _config_base.Config

    def _make_one(self):
        klass = self._get_target_class()
        return klass()

    def test_constructor(self):
        from ci_diff_helper import _utils

        klass = self._get_target_class()
        config = self._make_one()
        self.assertIsInstance(config, klass)
        self.assertIs(config._active, _utils.UNSET)

    def _active_helper(self, env_var, active_val):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        # Fake the environment variable on the instance.
        config._active_env_var = env_var
        # Make sure there is no _active value set.
        self.assertIs(config._active, _utils.UNSET)

        # Patch the helper so we can control the value.
        in_ci_patch = mock.patch(
            'ci_diff_helper._config_base._in_ci', return_value=active_val)
        with in_ci_patch as mocked:
            result = config.active
            self.assertIs(result, active_val)
            mocked.assert_called_once_with(env_var)

        return mocked, config

    def test_active_property(self):
        active_val = object()
        env_var = 'MY_CI'
        self._active_helper(env_var, active_val)

    def test_active_property_cache(self):
        active_val = object()
        env_var = 'MY_CI'
        mocked, config = self._active_helper(env_var, active_val)
        # Make sure the mock was only used once on first access.
        self.assertEqual(mocked.call_count, 1)
        # Test that the value is cached.
        self.assertIs(config._active, active_val)
        # Test that cached value is re-used.
        self.assertIs(config.active, active_val)
        # Make sure the mock did not get called again on future access.
        self.assertEqual(mocked.call_count, 1)

    def _branch_helper(self, env_var, branch_val):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        # Fake the environment variable on the instance.
        config._branch_env_var = env_var
        # Make sure there is no _branch value set.
        self.assertIs(config._branch, _utils.UNSET)

        # Patch the helper so we can control the value.
        ci_branch_patch = mock.patch(
            'ci_diff_helper._config_base._ci_branch',
            return_value=branch_val)
        with ci_branch_patch as mocked:
            result = config.branch
            self.assertIs(result, branch_val)
            mocked.assert_called_once_with(env_var)

        return mocked, config

    def test_branch_property(self):
        branch_val = 'branch-on-a-tree-in-a-forest'
        env_var = 'MY_CI'
        self._branch_helper(env_var, branch_val)

    def test_branch_property_cache(self):
        branch_val = 'make-tomorrow-a-tree'
        env_var = 'MY_CI'
        mocked, config = self._branch_helper(env_var, branch_val)
        # Make sure the mock was only used once on first access.
        self.assertEqual(mocked.call_count, 1)
        # Test that the value is cached.
        self.assertIs(config._branch, branch_val)
        # Test that cached value is re-used.
        self.assertIs(config.branch, branch_val)
        # Make sure the mock did not get called again on future access.
        self.assertEqual(mocked.call_count, 1)

    def test_branch_property_error(self):
        import mock

        config = self._make_one()
        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                getattr(config, 'branch')
