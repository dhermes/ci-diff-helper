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
    def _call_function_under_test(*args):
        from ci_diff_helper._utils import check_output
        return check_output(*args)

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
