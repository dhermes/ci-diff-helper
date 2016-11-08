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

    def _helper(self, env_var, value):
        import mock

        mock_env = {env_var: value}
        with mock.patch('os.environ', new=mock_env):
            return self._call_function_under_test(env_var)

    def test_success(self):
        env_var = 'MY_CI'
        self.assertTrue(self._helper(env_var, 'true'))

    def test_success_uppercase(self):
        env_var = 'MOI_SEE_OY'
        self.assertTrue(self._helper(env_var, 'True'))

    def test_failure_missing(self):
        import mock

        env_var = 'MY_CI'
        with mock.patch('os.environ', new={}):
            self.assertFalse(self._call_function_under_test(env_var))

    def test_failure_invalid(self):
        env_var = 'HI_BYE_CI'
        self.assertFalse(self._helper(env_var, 'Treeoooh'))


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
            with self.assertRaises(OSError):
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
        self.assertIs(config._branch, _utils.UNSET)
        self.assertIs(config._is_merge, _utils.UNSET)

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
            with self.assertRaises(OSError):
                getattr(config, 'branch')

    def _is_merge_helper(self, is_merge_val):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        # Make sure there is no _is_merge value set.
        self.assertIs(config._is_merge, _utils.UNSET)

        # Patch the helper so we can control the value.
        merge_commit_patch = mock.patch(
            'ci_diff_helper.git_tools.merge_commit',
            return_value=is_merge_val)
        with merge_commit_patch as mocked:
            result = config.is_merge
            if is_merge_val:
                self.assertTrue(result)
            else:
                self.assertFalse(result)
            mocked.assert_called_once_with()

        return mocked, config

    def test_is_merge_property(self):
        self._is_merge_helper(True)

    def test_is_merge_property_cache(self):
        mocked, config = self._is_merge_helper(False)
        # Make sure the mock was only used once on first access.
        self.assertEqual(mocked.call_count, 1)
        # Test that the value is cached.
        self.assertFalse(config._is_merge)
        # Test that cached value is re-used.
        self.assertFalse(config.is_merge)
        # Make sure the mock did not get called again on future access.
        self.assertEqual(mocked.call_count, 1)

    def _tag_helper(self, env_var, tag_val='', expected=None):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        # Fake the environment variable on the instance.
        config._tag_env_var = env_var
        # Make sure there is no _tag value set.
        self.assertIs(config._tag, _utils.UNSET)

        # Patch the environment so we can control the value.
        environ_patch = mock.patch(
            'os.environ', new={env_var: tag_val})
        with environ_patch:
            result = config.tag
            if expected is None:
                self.assertIsNone(result, expected)
            else:
                self.assertEqual(result, expected)

        return config

    def test_tag_property_unset(self):
        env_var = 'MY_CI'
        self._tag_helper(env_var)

    def test_tag_property_set(self):
        env_var = 'MY_CI'
        tag = '0.1.0'
        self._tag_helper(env_var, tag, tag)

    def test_tag_property_cache(self):
        env_var = 'MY_CI'
        tag = '0.0.144'
        config = self._tag_helper(env_var, tag, tag)
        # Test that the value is cached.
        self.assertEqual(config._tag, tag)
        # Test that cached value is re-used.
        self.assertEqual(config.tag, tag)

    def test___repr__(self):
        import mock

        config = self._make_one()
        with mock.patch('os.environ', new={}):
            self.assertEqual(repr(config), '<Config (active=False)>')
