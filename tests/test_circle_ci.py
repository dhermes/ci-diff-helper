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


class Test__circle_ci_pr(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import circle_ci
        return circle_ci._circle_ci_pr()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        valid_int = '331'
        actual_val = 331
        self.assertEqual(int(valid_int), actual_val)
        mock_env = {env.CIRCLE_CI_PR_NUM: valid_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertEqual(self._call_function_under_test(), actual_val)

    def test_failure_unset(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertIsNone(self._call_function_under_test())

    def test_failure_bad_value(self):
        import mock
        from ci_diff_helper import environment_vars as env

        not_int = 'not-int'
        self.assertRaises(ValueError, int, not_int)
        mock_env = {env.CIRCLE_CI_PR_NUM: not_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertIsNone(self._call_function_under_test())


class Test__repo_url(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper import circle_ci
        return circle_ci._repo_url()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        repo_url = 'https://github.com/foo/bar'
        mock_env = {env.CIRCLE_CI_REPO_URL: repo_url}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertEqual(result, repo_url)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(OSError):
                self._call_function_under_test()


class Test__provider_slug(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(repo_url):
        from ci_diff_helper import circle_ci
        return circle_ci._provider_slug(repo_url)

    def test_github(self):
        from ci_diff_helper import circle_ci

        repo_url = 'https://github.com/hi/goodbye'
        provider, slug = self._call_function_under_test(repo_url)
        self.assertIs(provider, circle_ci.CircleCIRepoProvider.github)
        self.assertEqual(slug, 'hi/goodbye')

    def test_github_bad_prefix(self):
        with self.assertRaises(ValueError):
            self._call_function_under_test('http://github.com/org/repo')

    def test_bitbucket(self):
        from ci_diff_helper import circle_ci

        repo_url = 'https://bitbucket.org/fly/on-the-wall'
        provider, slug = self._call_function_under_test(repo_url)
        self.assertIs(provider, circle_ci.CircleCIRepoProvider.bitbucket)
        self.assertEqual(slug, 'fly/on-the-wall')

    def test_bitbucket_bad_prefix(self):
        with self.assertRaises(ValueError):
            self._call_function_under_test('http://bitbucket.org/user/proj')

    def test_bad_url(self):
        with self.assertRaises(ValueError):
            self._call_function_under_test('nope')


class TestCircleCIRepoProvider(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import circle_ci
        return circle_ci.CircleCIRepoProvider

    def _make_one(self, enum_val):
        klass = self._get_target_class()
        return klass(enum_val)

    def test_members(self):
        klass = self._get_target_class()
        self.assertEqual(
            set([enum_val.name for enum_val in klass]),
            set(['bitbucket', 'github']))

    def test_bitbucket(self):
        klass = self._get_target_class()
        provider_obj = self._make_one('bitbucket')
        self.assertIs(provider_obj, klass.bitbucket)

    def test_github(self):
        klass = self._get_target_class()
        provider_obj = self._make_one('github')
        self.assertIs(provider_obj, klass.github)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            self._make_one('mustard')


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
        self.assertIs(config._base, _utils.UNSET)
        self.assertIs(config._branch, _utils.UNSET)
        self.assertIs(config._is_merge, _utils.UNSET)
        self.assertIs(config._pr, _utils.UNSET)
        self.assertIs(config._pr_info_cached, _utils.UNSET)
        self.assertIs(config._provider, _utils.UNSET)
        self.assertIs(config._repo_url, _utils.UNSET)
        self.assertIs(config._slug, _utils.UNSET)
        self.assertIs(config._tag, _utils.UNSET)

    def test___repr__(self):
        import mock

        config = self._make_one()
        with mock.patch('os.environ', new={}):
            self.assertEqual(repr(config), '<CircleCI (active=False)>')

    def _pr_helper(self, pr_val):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        # Make sure there is no _pr value set.
        self.assertIs(config._pr, _utils.UNSET)

        # Patch the helper so we can control the value.
        travis_pr_patch = mock.patch(
            'ci_diff_helper.circle_ci._circle_ci_pr', return_value=pr_val)
        with travis_pr_patch as mocked:
            result = config.pr
            self.assertIs(result, pr_val)
            mocked.assert_called_once_with()

        return config

    def test_pr_property(self):
        pr_val = 1337
        self._pr_helper(pr_val)

    def test_pr_property_cache(self):
        pr_val = 42043
        config = self._pr_helper(pr_val)
        # Test that the value is cached.
        self.assertIs(config._pr, pr_val)
        # Test that cached value is re-used.
        self.assertIs(config.pr, pr_val)

    def test_in_pr_property(self):
        config = self._make_one()
        # Patch with an actual PR.
        config._pr = 1337
        self.assertTrue(config.in_pr)

    def test_in_pr_property_fails(self):
        config = self._make_one()
        # Patch a missing PR.
        config._pr = None
        self.assertFalse(config.in_pr)

    def _repo_url_helper(self, repo_url_val):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        # Make sure there is no _repo_url value set.
        self.assertIs(config._repo_url, _utils.UNSET)

        # Patch the helper so we can control the value.
        repo_url_patch = mock.patch(
            'ci_diff_helper.circle_ci._repo_url',
            return_value=repo_url_val)
        with repo_url_patch as mocked:
            result = config.repo_url
            self.assertIs(result, repo_url_val)
            mocked.assert_called_once_with()

        return config

    def test_repo_url_property(self):
        repo_url_val = 'reap-oh-no-you-are-elle'
        self._repo_url_helper(repo_url_val)

    def test_repo_url_property_cache(self):
        repo_url_val = 'read-poem-earl'
        config = self._repo_url_helper(repo_url_val)
        # Test that the value is cached.
        self.assertIs(config._repo_url, repo_url_val)
        # Test that cached value is re-used.
        self.assertIs(config.repo_url, repo_url_val)

    def _slug_provider_helper(self, provider_val, slug_val, slug_first=False):
        import mock
        from ci_diff_helper import _utils

        config = self._make_one()
        config._repo_url = mock.sentinel.repo_url
        # Make sure there is no _provider value set.
        self.assertIs(config._provider, _utils.UNSET)

        # Patch the helper so we can control the value.
        provider_patch = mock.patch(
            'ci_diff_helper.circle_ci._provider_slug',
            return_value=(provider_val, slug_val))
        with provider_patch as mocked:
            if slug_first:
                self.assertIs(config.slug, slug_val)
                self.assertIs(config.provider, provider_val)
            else:
                self.assertIs(config.provider, provider_val)
                self.assertIs(config.slug, slug_val)
            mocked.assert_called_once_with(mock.sentinel.repo_url)

        return config

    def test_provider_property(self):
        provider_val = 'pro-divide-uhr'
        self._slug_provider_helper(provider_val, None)

    def test_provider_property_cache(self):
        provider_val = 'pro-bono-vide'
        config = self._slug_provider_helper(provider_val, None)
        # Test that the value is cached.
        self.assertIs(config._provider, provider_val)
        # Test that cached value is re-used.
        self.assertIs(config.provider, provider_val)

    def test_slug_property(self):
        slug_val = 'slug-slugger-sluggest'
        self._slug_provider_helper(None, slug_val, slug_first=True)

    def test_slug_property_cache(self):
        slug_val = 'soup'
        config = self._slug_provider_helper(
            None, slug_val, slug_first=True)
        # Test that the value is cached.
        self.assertIs(config._slug, slug_val)
        # Test that cached value is re-used.
        self.assertIs(config.slug, slug_val)

    def test__pr_info_property_cache(self):
        import mock

        config = self._make_one()
        config._pr_info_cached = mock.sentinel.info

        self.assertIs(config._pr_info, mock.sentinel.info)

    def test__pr_info_property_non_pr(self):
        from ci_diff_helper import _utils

        config = self._make_one()

        # Fake that there is no PR.
        config._pr = None
        self.assertIsNone(config.pr)

        # Make sure the cached value isn't set.
        self.assertIs(config._pr_info_cached, _utils.UNSET)

        # Now compute the property value.
        self.assertEqual(config._pr_info, {})

    def test__pr_info_property_github_pr(self):
        import mock
        from ci_diff_helper import circle_ci
        from ci_diff_helper import environment_vars as env

        config = self._make_one()

        slug = 'arf/garf'
        repo_url = circle_ci._GITHUB_PREFIX + slug
        pr_id = 223311
        mock_env = {
            env.CIRCLE_CI_REPO_URL: repo_url,
            env.CIRCLE_CI_PR_NUM: str(pr_id),
        }
        with mock.patch('os.environ', new=mock_env):
            with mock.patch('ci_diff_helper._github.pr_info',
                            return_value=mock.sentinel.info) as get_info:
                pr_info = config._pr_info
                self.assertIs(pr_info, mock.sentinel.info)
                get_info.assert_called_once_with(slug, pr_id)

        self.assertEqual(get_info.call_count, 1)
        # Make sure value is cached and doesn't call the helper again.
        self.assertIs(pr_info, mock.sentinel.info)
        self.assertEqual(get_info.call_count, 1)

    def test__pr_info_property_pr_not_github(self):
        import mock
        from ci_diff_helper import circle_ci
        from ci_diff_helper import environment_vars as env

        config = self._make_one()

        slug = 'bucket/chuck-it'
        repo_url = circle_ci._BITBUCKET_PREFIX + slug
        mock_env = {
            env.CIRCLE_CI_REPO_URL: repo_url,
            env.CIRCLE_CI_PR_NUM: '817',
        }
        with mock.patch('os.environ', new=mock_env):
            with mock.patch('ci_diff_helper._github.pr_info') as get_info:
                with self.assertRaises(NotImplementedError):
                    getattr(config, '_pr_info')
                get_info.assert_not_called()

    def test_base_property_cache(self):
        import mock

        config = self._make_one()
        config._base = mock.sentinel.base

        self.assertIs(config.base, mock.sentinel.base)

    def test_base_property_non_pr(self):
        config = self._make_one()
        # Fake that we are outside a PR.
        config._pr = None

        with self.assertRaises(NotImplementedError):
            getattr(config, 'base')

    def test_base_property_success(self):
        config = self._make_one()
        # Fake that we are inside a PR.
        config._pr = 123
        base_sha = '23ff39e7f437d888cb1aa07b4646fc6376f4af35'
        payload = {'base': {'sha': base_sha}}
        config._pr_info_cached = payload

        self.assertEqual(config.base, base_sha)

    def test_base_property_pr_bad_payload(self):
        config = self._make_one()
        # Fake that we are inside a PR.
        config._pr = 678
        config._pr_info_cached = {}
        # Also fake the info that shows up in the exception.
        config._slug = 'foo/food'

        with self.assertRaises(KeyError):
            getattr(config, 'base')
