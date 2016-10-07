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

import os
import unittest

from tests import utils


class Test_in_travis(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import in_travis
        return in_travis()

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


class Test_in_travis_pr(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import in_travis_pr
        return in_travis_pr()

    def test_success(self):
        import mock
        from ci_diff_helper import travis

        valid_int = '1234'
        self.assertEqual(int(valid_int), 1234)
        mock_env = {travis._TRAVIS_PR_ENV: valid_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertTrue(self._call_function_under_test())

    def test_failure_unset(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertFalse(self._call_function_under_test())

    def test_failure_bad_value(self):
        import mock
        from ci_diff_helper import travis

        not_int = 'not-int'
        self.assertRaises(ValueError, int, not_int)
        mock_env = {travis._TRAVIS_PR_ENV: not_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertFalse(self._call_function_under_test())


class Test_travis_branch(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import travis_branch
        return travis_branch()

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


class Test_git_root(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import git_root
        return git_root()

    def test_sys_call(self):
        import mock

        with mock.patch('ci_diff_helper._utils.check_output') as mocked:
            result = self._call_function_under_test()
            self.assertIs(result, mocked.return_value)
            mocked.assert_called_once_with(
                'git', 'rev-parse', '--show-toplevel')

    @unittest.skipUnless(utils.HAS_GIT, 'git not installed')
    def test_actual_call(self):
        result = self._call_function_under_test()
        result = os.path.abspath(result)  # Normalize path for Windows.
        tests_dir = os.path.dirname(__file__)
        root_dir = os.path.abspath(os.path.join(tests_dir, '..'))
        self.assertEqual(result, root_dir)


class Test_get_checked_in_files(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import get_checked_in_files
        return get_checked_in_files()

    @staticmethod
    def _do_nothing(value):
        return value

    def test_it(self):
        import mock

        filenames = [
            'a.py',
            'shell-not-py.sh',
            os.path.join('b', 'c.py'),
            'Makefile',
            os.path.join('d', 'e', 'f.py'),
        ]
        cmd_output = '\n'.join(filenames)
        mock_output = mock.patch('ci_diff_helper._utils.check_output',
                                 return_value=cmd_output)

        git_root = os.path.join('totally', 'on', 'your', 'filesystem')
        mock_root = mock.patch('ci_diff_helper.git_root',
                               return_value=git_root)

        mock_abspath = mock.patch('os.path.abspath', new=self._do_nothing)

        with mock_abspath:
            with mock_root:
                with mock_output as mocked:
                    result = self._call_function_under_test()
                    mocked.assert_called_once_with(
                        'git', 'ls-files', git_root)
                    self.assertEqual(result, filenames)

    @staticmethod
    def _all_files(root_dir):
        result = set()
        for dirname, _, filenames in os.walk(root_dir):
            for filename in filenames:
                result.add(os.path.join(dirname, filename))
        return result

    @unittest.skipUnless(utils.HAS_GIT, 'git not installed')
    def test_actual_call(self):
        result = self._call_function_under_test()
        tests_dir = os.path.dirname(__file__)
        root_dir = os.path.abspath(os.path.join(tests_dir, '..'))
        self.assertLessEqual(set(result), self._all_files(root_dir))
