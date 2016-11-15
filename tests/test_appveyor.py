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


class Test__appveyor_provider(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.appveyor import _appveyor_provider
        return _appveyor_provider()

    def _helper(self, repo_provider):
        import mock
        from ci_diff_helper import environment_vars as env

        mock_env = {env.APPVEYOR_REPO: repo_provider}
        with mock.patch('os.environ', new=mock_env):
            return self._call_function_under_test()

    def test_success(self):
        from ci_diff_helper import appveyor

        result = self._helper('bitbucket')
        self.assertIs(result, appveyor.AppVeyorRepoProvider.bitbucket)

    def test_success_different_case(self):
        from ci_diff_helper import appveyor

        result = self._helper('gitHub')
        self.assertIs(result, appveyor.AppVeyorRepoProvider.github)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(ValueError):
                self._call_function_under_test()


class TestAppVeyorRepoProvider(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import appveyor
        return appveyor.AppVeyorRepoProvider

    def _make_one(self, enum_val):
        klass = self._get_target_class()
        return klass(enum_val.lower())

    def test_members(self):
        klass = self._get_target_class()
        self.assertEqual(
            set([enum_val.name for enum_val in klass]),
            set(['bitbucket', 'github', 'gitlab', 'kiln', 'vso']))

    def test_bitbucket(self):
        klass = self._get_target_class()
        provider_obj = self._make_one('bitbucket')
        self.assertIs(provider_obj, klass.bitbucket)

    def test_github(self):
        klass = self._get_target_class()
        provider_obj = self._make_one('gitHub')
        self.assertIs(provider_obj, klass.github)

    def test_gitlab(self):
        klass = self._get_target_class()
        provider_obj = self._make_one('gitlab')
        self.assertIs(provider_obj, klass.gitlab)

    def test_kiln(self):
        klass = self._get_target_class()
        provider_obj = self._make_one('kiln')
        self.assertIs(provider_obj, klass.kiln)

    def test_vso(self):
        klass = self._get_target_class()
        provider_obj = self._make_one('vso')
        self.assertIs(provider_obj, klass.vso)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            self._make_one('ketchup')


class TestAppVeyor(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import appveyor
        return appveyor.AppVeyor

    def _make_one(self):
        klass = self._get_target_class()
        return klass()

    def test_constructor(self):
        from ci_diff_helper import _utils

        klass = self._get_target_class()
        config = self._make_one()
        self.assertIsInstance(config, klass)
        self.assertIs(config._provider, _utils.UNSET)

    def _provider_helper(self, provider_val):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        # Make sure there is no _provider value set.
        self.assertIs(config._provider, _utils.UNSET)

        # Patch the helper so we can control the value.
        provider_patch = mock.patch(
            'ci_diff_helper.appveyor._appveyor_provider',
            return_value=provider_val)
        with provider_patch as mocked:
            result = config.provider
            self.assertIs(result, provider_val)
            mocked.assert_called_once_with()

        return config

    def test_provider_property(self):
        from ci_diff_helper.appveyor import AppVeyorRepoProvider

        provider_val = AppVeyorRepoProvider.github
        self._provider_helper(provider_val)

    def test_provider_property_cache(self):
        from ci_diff_helper.appveyor import AppVeyorRepoProvider

        provider_val = AppVeyorRepoProvider.gitlab
        config = self._provider_helper(provider_val)
        # Test that the value is cached.
        self.assertIs(config._provider, provider_val)
        # Test that cached value is re-used.
        self.assertIs(config.provider, provider_val)

    def test_tag_property(self):
        # NOTE: This method is only needed for test coverage. The defined
        #       do-nothing tag property is there to modify the docstring
        #       of the original.
        config = self._make_one()
        tag = '0.x.y'
        config._tag = tag
        self.assertEqual(config.tag, tag)

    def test___repr__(self):
        import mock
        from ci_diff_helper import environment_vars as env

        config = self._make_one()

        mock_env = {env.IN_APPVEYOR: 'false'}
        with mock.patch('os.environ', new=mock_env):
            self.assertEqual(repr(config), '<AppVeyor (active=False)>')
