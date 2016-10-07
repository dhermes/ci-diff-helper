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


class Test_in_travis(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import in_travis
        return in_travis()

    def test_success(self):
        import mock
        import ci_diff_helper

        mock_env = {ci_diff_helper._IN_TRAVIS_ENV: 'true'}
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
        import ci_diff_helper

        valid_int = '1234'
        self.assertEqual(int(valid_int), 1234)
        mock_env = {ci_diff_helper._TRAVIS_PR_ENV: valid_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertTrue(self._call_function_under_test())

    def test_failure_unset(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertFalse(self._call_function_under_test())

    def test_failure_bad_value(self):
        import mock
        import ci_diff_helper

        not_int = 'not-int'
        self.assertRaises(ValueError, int, not_int)
        mock_env = {ci_diff_helper._TRAVIS_PR_ENV: not_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertFalse(self._call_function_under_test())


class Test_travis_branch(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import travis_branch
        return travis_branch()

    def test_success(self):
        import mock
        import ci_diff_helper

        branch = 'this-very-branch'
        mock_env = {ci_diff_helper._TRAVIS_BRANCH_ENV: branch}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertEqual(result, branch)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(OSError):
                self._call_function_under_test()
