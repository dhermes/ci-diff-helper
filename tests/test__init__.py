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


class Test_get_config(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import get_config
        return get_config()

    def test_none(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(OSError):
                self._call_function_under_test()

    def test_multiple(self):
        import mock
        from ci_diff_helper import environment_vars as env

        mock_env = {
            env.IN_CIRCLE_CI: 'true',
            env.IN_APPVEYOR: 'True',
        }
        with mock.patch('os.environ', new=mock_env):
            with self.assertRaises(OSError):
                self._call_function_under_test()

    def test_match(self):
        import mock
        from ci_diff_helper import environment_vars as env
        from ci_diff_helper import travis

        mock_env = {env.IN_TRAVIS: 'true'}
        with mock.patch('os.environ', new=mock_env):
            config = self._call_function_under_test()

        self.assertIsInstance(config, travis.Travis)
