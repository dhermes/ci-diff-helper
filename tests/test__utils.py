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


class Test_check_output(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(*args, **kwargs):
        from ci_diff_helper._utils import check_output
        return check_output(*args, **kwargs)

    def _helper(self, ret_val, expected_result):
        import mock

        arg1 = 'foo'
        arg2 = 'bar'
        check_mock = mock.patch('subprocess.check_output',
                                return_value=ret_val)
        with check_mock as mocked:
            result = self._call_function_under_test(arg1, arg2)
            mocked.assert_called_once_with((arg1, arg2))
            self.assertEqual(result, expected_result)

    def test_bytes(self):
        ret_val = b'abc\n'
        expected_result = u'abc'
        self._helper(ret_val, expected_result)

    def test_unicode(self):
        ret_val = b'abc\n\tab'
        expected_result = u'abc\n\tab'
        self._helper(ret_val, expected_result)

    def _err_helper(self, ignore_err=False):
        import subprocess
        import mock

        kwargs = {}
        if ignore_err:
            kwargs['ignore_err'] = True
        check_mock = mock.patch(
            'subprocess.check_output',
            side_effect=subprocess.CalledProcessError(1, ''))

        arg = 'hello-is-it-me'
        with check_mock as mocked:
            result = self._call_function_under_test(arg, **kwargs)
            # We can only get here in the ignore_err case.
            mocked.assert_called_once_with(
                (arg,), stderr=subprocess.PIPE)
            self.assertIsNone(result)

    def test_ignore_err(self):
        self._err_helper(ignore_err=True)

    def test_uncaught_err(self):
        import subprocess

        with self.assertRaises(subprocess.CalledProcessError):
            self._err_helper()

    def test_bad_keywords(self):
        with self.assertRaises(TypeError):
            self._call_function_under_test(huh='bad-kw')


class Test_pr_from_commit(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(merge_subject):
        from ci_diff_helper._utils import pr_from_commit
        return pr_from_commit(merge_subject)

    def test_no_id(self):
        subject = 'No pound sign.'
        result = self._call_function_under_test(subject)
        self.assertIsNone(result)

    def test_too_many_ids(self):
        subject = '#1234 then #5678 too many.'
        result = self._call_function_under_test(subject)
        self.assertIsNone(result)

    def test_non_int_id(self):
        subject = '#x will not match the regex.'
        result = self._call_function_under_test(subject)
        self.assertIsNone(result)

    def test_valid_id(self):
        expected = 88901
        subject = 'Merge pull request #%d from queso/cheese' % (expected,)
        result = self._call_function_under_test(subject)
        self.assertEqual(result, expected)


class Test__in_ci(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(env_var):
        from ci_diff_helper._utils import _in_ci
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
        from ci_diff_helper._utils import _ci_branch
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
        from ci_diff_helper import _utils
        return _utils.Config

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
            'ci_diff_helper._utils._in_ci', return_value=active_val)
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
            'ci_diff_helper._utils._ci_branch',
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
