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
