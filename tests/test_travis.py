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


class Test__in_travis(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _in_travis
        return _in_travis()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        mock_env = {env.IN_TRAVIS_ENV: 'true'}
        with mock.patch('os.environ', new=mock_env):
            self.assertTrue(self._call_function_under_test())

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertFalse(self._call_function_under_test())


class Test__travis_pr(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _travis_pr
        return _travis_pr()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        valid_int = '1234'
        actual_val = 1234
        self.assertEqual(int(valid_int), actual_val)
        mock_env = {env.TRAVIS_PR_ENV: valid_int}
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
        mock_env = {env.TRAVIS_PR_ENV: not_int}
        with mock.patch('os.environ', new=mock_env):
            self.assertIsNone(self._call_function_under_test())


class Test__travis_branch(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _travis_branch
        return _travis_branch()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        branch = 'this-very-branch'
        mock_env = {env.TRAVIS_BRANCH_ENV: branch}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertEqual(result, branch)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                self._call_function_under_test()


class Test__travis_event_type(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _travis_event_type
        return _travis_event_type()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env
        from ci_diff_helper import travis

        event_env = 'push'
        mock_env = {env.TRAVIS_EVENT_TYPE_ENV: event_env}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertIs(result, travis.TravisEventType.push)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(ValueError):
                self._call_function_under_test()


class Test__get_commit_range(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _get_commit_range
        return _get_commit_range()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env
        from ci_diff_helper import travis

        start = 'abcd'
        finish = 'wxyz'
        commit_range = start + travis._RANGE_DELIMITER + finish
        mock_env = {env.TRAVIS_RANGE_ENV: commit_range}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertEqual(result, (start, finish))

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                self._call_function_under_test()


class Test__verify_merge_base(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(start, finish):
        from ci_diff_helper.travis import _verify_merge_base
        return _verify_merge_base(start, finish)

    def test_success(self):
        import mock

        start = 'abcd'
        finish = 'wxyz'
        output_mock = mock.patch('ci_diff_helper._utils.check_output',
                                 return_value=start)
        with output_mock as mocked:
            result = self._call_function_under_test(start, finish)
            self.assertIsNone(result)
            mocked.assert_called_once_with(
                'git', 'merge-base', start, finish, ignore_err=True)

    def _failure_helper(self, start, merge_base):
        import mock

        finish = 'wxyz'
        output_mock = mock.patch('ci_diff_helper._utils.check_output',
                                 return_value=merge_base)
        with output_mock as mocked:
            with self.assertRaises(ValueError):
                self._call_function_under_test(start, finish)
            mocked.assert_called_once_with(
                'git', 'merge-base', start, finish, ignore_err=True)

    def test_failure_sys_call_bad_base(self):
        start = 'abcd'
        merge_base = 'not-start'
        self.assertNotEqual(start, merge_base)
        self._failure_helper(start, merge_base)

    def test_failure_sys_call_error(self):
        start = 'abcd'
        # A "merge_base=None" indicates the system call failed.
        self._failure_helper(start, None)


class Test__get_merge_base_from_github(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(slug, start, finish):
        from ci_diff_helper.travis import _get_merge_base_from_github
        return _get_merge_base_from_github(slug, start, finish)

    def test_success(self):
        import mock

        sha = 'f8c2476b625f6a6f35a9e7f4d566c9b036722f11'
        payload = {
            'merge_base_commit': {
                'sha': sha,
            },
        }
        slug = 'a/b'
        start = '1234'
        finish = '6789'

        compare_patch = mock.patch(
            'ci_diff_helper._github.commit_compare',
            return_value=payload)
        with compare_patch as mocked:
            result = self._call_function_under_test(slug, start, finish)
            self.assertEqual(result, sha)
            mocked.assert_called_once_with(slug, start, finish)

    def test_failure(self):
        import mock

        slug = 'a/b'
        start = '1234'
        finish = '6789'

        compare_patch = mock.patch(
            'ci_diff_helper._github.commit_compare',
            return_value={})
        with compare_patch as mocked:
            with self.assertRaises(KeyError):
                self._call_function_under_test(slug, start, finish)
            mocked.assert_called_once_with(slug, start, finish)


class Test__push_build_base(unittest.TestCase):

    @staticmethod
    def _call_function_under_test(slug):
        from ci_diff_helper.travis import _push_build_base
        return _push_build_base(slug)

    def test_unresolved_start_commit(self):
        import mock

        start = 'abcd'
        finish = 'wxyz'
        slug = 'raindrops/roses'
        patch_range = mock.patch(
            'ci_diff_helper.travis._get_commit_range',
            return_value=(start, finish))
        # Make sure ``start_full`` is empty, indicating that the
        # local ``git`` checkout doesn't have the commit.
        patch_output = mock.patch(
            'ci_diff_helper._utils.check_output',
            return_value=None)
        # Make sure ``start_full`` is empty, indicating that the
        # local ``git`` checkout doesn't have the commit.
        sha = '058b526c33dea1e8fc7013b498593cd106300411'
        patch_from_github = mock.patch(
            'ci_diff_helper.travis._get_merge_base_from_github',
            return_value=sha)

        with patch_range as mocked_range:
            with patch_output as mocked_output:
                with patch_from_github as mocked:
                    result = self._call_function_under_test(slug)
                    self.assertEqual(result, sha)
                    mocked.called_once_with(slug, start, finish)
                    mocked_output.assert_called_once_with(
                        'git', 'rev-parse', start, ignore_err=True)
                    mocked_range.assert_called_once_with()

    def test_success(self):
        import mock

        start = 'abcd'
        start_full = 'abcd-zomg-more'
        finish = 'wxyz'
        patch_range = mock.patch(
            'ci_diff_helper.travis._get_commit_range',
            return_value=(start, finish))
        # Just hide the verification / make it do nothing.
        patch_verify = mock.patch(
            'ci_diff_helper.travis._verify_merge_base')
        # Make sure ``start_full`` is empty, indicating that the
        # local ``git`` checkout doesn't have the commit.
        patch_output = mock.patch(
            'ci_diff_helper._utils.check_output',
            return_value=start_full)

        with patch_range as mocked_range:
            with patch_verify as mocked_verify:
                with patch_output as mocked:
                    result = self._call_function_under_test(None)
                    self.assertEqual(result, start_full)
                    mocked.assert_called_once_with(
                        'git', 'rev-parse', start, ignore_err=True)
                    mocked_verify.assert_called_once_with(start_full, finish)
                    mocked_range.assert_called_once_with()


class Test__travis_slug(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import _travis_slug
        return _travis_slug()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        slug = 'foo/bar'
        mock_env = {env.TRAVIS_SLUG_ENV: slug}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertEqual(result, slug)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                self._call_function_under_test()


class TravisEventType(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import travis
        return travis.TravisEventType

    def _make_one(self, enum_val):
        klass = self._get_target_class()
        return klass(enum_val)

    def test_members(self):
        klass = self._get_target_class()
        self.assertEqual(
            set([enum_val.name for enum_val in klass]),
            set(['api', 'cron', 'pull_request', 'push']))

    def test_api(self):
        klass = self._get_target_class()
        enum_obj = self._make_one('api')
        self.assertIs(enum_obj, klass.api)

    def test_cron(self):
        klass = self._get_target_class()
        enum_obj = self._make_one('cron')
        self.assertIs(enum_obj, klass.cron)

    def test_pull_request(self):
        klass = self._get_target_class()
        enum_obj = self._make_one('pull_request')
        self.assertIs(enum_obj, klass.pull_request)

    def test_push(self):
        klass = self._get_target_class()
        enum_obj = self._make_one('push')
        self.assertIs(enum_obj, klass.push)


class TestTravis(unittest.TestCase):

    @staticmethod
    def _get_target_class():
        from ci_diff_helper import travis
        return travis.Travis

    def _make_one(self):
        klass = self._get_target_class()
        return klass()

    def test_constructor(self):
        from ci_diff_helper import travis

        klass = self._get_target_class()
        config = self._make_one()
        self.assertIsInstance(config, klass)
        self.assertIs(config._active, travis._UNSET)
        self.assertIs(config._pr, travis._UNSET)

    def _active_helper(self, active_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _active value set.
        self.assertIs(config._active, travis._UNSET)

        # Patch the helper so we can control the value.
        in_travis_patch = mock.patch(
            'ci_diff_helper.travis._in_travis', return_value=active_val)
        with in_travis_patch as mocked:
            result = config.active
            self.assertIs(result, active_val)
            mocked.assert_called_once_with()

        return config

    def test_active_property(self):
        active_val = object()
        self._active_helper(active_val)

    def test_active_property_cache(self):
        active_val = object()
        config = self._active_helper(active_val)
        # Test that the value is cached.
        self.assertIs(config._active, active_val)
        # Test that cached value is re-used.
        self.assertIs(config.active, active_val)

    def _pr_helper(self, pr_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _pr value set.
        self.assertIs(config._pr, travis._UNSET)

        # Patch the helper so we can control the value.
        travis_pr_patch = mock.patch(
            'ci_diff_helper.travis._travis_pr', return_value=pr_val)
        with travis_pr_patch as mocked:
            result = config.pr
            self.assertIs(result, pr_val)
            mocked.assert_called_once_with()

        return config

    def test_pr_property(self):
        pr_val = 1337
        self._pr_helper(pr_val)

    def test_pr_property_cache(self):
        pr_val = 42
        config = self._pr_helper(pr_val)
        # Test that the value is cached.
        self.assertIs(config._pr, pr_val)
        # Test that cached value is re-used.
        self.assertIs(config.pr, pr_val)

    def _branch_helper(self, branch_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _branch value set.
        self.assertIs(config._branch, travis._UNSET)

        # Patch the helper so we can control the value.
        in_travis_patch = mock.patch(
            'ci_diff_helper.travis._travis_branch',
            return_value=branch_val)
        with in_travis_patch as mocked:
            result = config.branch
            self.assertIs(result, branch_val)
            mocked.assert_called_once_with()

        return config

    def test_branch_property(self):
        branch_val = 'branch-on-a-tree-in-a-forest'
        self._branch_helper(branch_val)

    def test_branch_property_cache(self):
        branch_val = 'make-tomorrow-a-tree'
        config = self._branch_helper(branch_val)
        # Test that the value is cached.
        self.assertIs(config._branch, branch_val)
        # Test that cached value is re-used.
        self.assertIs(config.branch, branch_val)

    def test_branch_property_error(self):
        import mock

        config = self._make_one()
        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                getattr(config, 'branch')

    def test_base_property_in_pr(self):
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure the Travis config thinks we are in a PR.
        config._event_type = travis.TravisEventType.pull_request
        self.assertTrue(config.in_pr)
        # Make sure the Travis config knows the current branch.
        branch = 'scary-tree-branch'
        config._branch = branch
        self.assertEqual(config.branch, branch)
        # Check that in the PR case, the base is a branch.
        self.assertIs(config._base, travis._UNSET)
        self.assertEqual(config.base, branch)
        # Verify that caching works.
        self.assertEqual(config._base, branch)
        self.assertEqual(config.base, branch)

    def test_base_property_push(self):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure the Travis config thinks we are in a push build.
        config._event_type = travis.TravisEventType.push
        self.assertFalse(config.in_pr)
        self.assertIs(config.event_type, travis.TravisEventType.push)
        # Make sure the Travis slug is set.
        slug = 'rainbows/puppies'
        config._slug = slug
        self.assertEqual(config.slug, slug)
        # Check that in the "push" case, the base gets set
        # from _push_build_base().
        base_val = '076879d777af62e621c9f72d2b5f6863e88689e9'
        push_base_patch = mock.patch(
            'ci_diff_helper.travis._push_build_base',
            return_value=base_val)
        self.assertIs(config._base, travis._UNSET)
        with push_base_patch as mocked:
            self.assertEqual(config.base, base_val)
            mocked.assert_called_once_with(slug)
        # Verify that caching works.
        self.assertEqual(config._base, base_val)
        self.assertEqual(config.base, base_val)

    def test_base_property_unsupported(self):
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure the Travis config thinks we are not in a PR.
        config._event_type = travis.TravisEventType.cron
        self.assertFalse(config.in_pr)
        # Verify the failure.
        with self.assertRaises(NotImplementedError):
            getattr(config, 'base')

    def _event_type_helper(self, event_type_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _event_type value set.
        self.assertIs(config._event_type, travis._UNSET)

        # Patch the helper so we can control the value.
        in_travis_patch = mock.patch(
            'ci_diff_helper.travis._travis_event_type',
            return_value=event_type_val)
        with in_travis_patch as mocked:
            result = config.event_type
            self.assertIs(result, event_type_val)
            mocked.assert_called_once_with()

        return config

    def test_event_type_property(self):
        event_type_val = 'push'
        self._event_type_helper(event_type_val)

    def test_event_type_property_cache(self):
        event_type_val = 'cron'
        config = self._event_type_helper(event_type_val)
        # Test that the value is cached.
        self.assertIs(config._event_type, event_type_val)
        # Test that cached value is re-used.
        self.assertIs(config.event_type, event_type_val)

    def _slug_helper(self, slug_val):
        import mock
        from ci_diff_helper import travis

        config = self._make_one()
        # Make sure there is no _slug value set.
        self.assertIs(config._slug, travis._UNSET)

        # Patch the helper so we can control the value.
        slug_patch = mock.patch(
            'ci_diff_helper.travis._travis_slug',
            return_value=slug_val)
        with slug_patch as mocked:
            result = config.slug
            self.assertIs(result, slug_val)
            mocked.assert_called_once_with()

        return config

    def test_slug_property(self):
        slug_val = 'slug-on-a-tree-in-a-forest'
        self._slug_helper(slug_val)

    def test_slug_property_cache(self):
        slug_val = 'slugging-along'
        config = self._slug_helper(slug_val)
        # Test that the value is cached.
        self.assertIs(config._slug, slug_val)
        # Test that cached value is re-used.
        self.assertIs(config.slug, slug_val)

    def test_slug_property_error(self):
        import mock

        config = self._make_one()
        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                getattr(config, 'slug')


class Test_in_travis(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import in_travis
        return in_travis()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        mock_env = {env.IN_TRAVIS_ENV: 'true'}
        with mock.patch('os.environ', new=mock_env):
            self.assertTrue(self._call_function_under_test())

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            self.assertFalse(self._call_function_under_test())


class Test_in_travis_pr(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import in_travis_pr
        return in_travis_pr()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        mock_env = {env.TRAVIS_EVENT_TYPE_ENV: 'pull_request'}
        with mock.patch('os.environ', new=mock_env):
            self.assertTrue(self._call_function_under_test())

    def test_failure_unset(self):
        import mock

        with self.assertRaises(ValueError):
            with mock.patch('os.environ', new={}):
                self.assertFalse(self._call_function_under_test())

    def test_failure_bad_value(self):
        import mock
        from ci_diff_helper import environment_vars as env

        mock_env = {env.TRAVIS_EVENT_TYPE_ENV: 'push'}
        with mock.patch('os.environ', new=mock_env):
            self.assertFalse(self._call_function_under_test())


class Test_travis_branch(unittest.TestCase):

    @staticmethod
    def _call_function_under_test():
        from ci_diff_helper.travis import travis_branch
        return travis_branch()

    def test_success(self):
        import mock
        from ci_diff_helper import environment_vars as env

        branch = 'this-very-branch'
        mock_env = {env.TRAVIS_BRANCH_ENV: branch}
        with mock.patch('os.environ', new=mock_env):
            result = self._call_function_under_test()
            self.assertEqual(result, branch)

    def test_failure(self):
        import mock

        with mock.patch('os.environ', new={}):
            with self.assertRaises(EnvironmentError):
                self._call_function_under_test()
