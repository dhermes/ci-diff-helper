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
