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

"""Shared utilities for ci-diff-helper."""

import os
import re
import subprocess


_PR_ID_REGEX = re.compile(r'#(\d+)')
_BRANCH_ERR_TEMPLATE = (
    'Build does not have an associated branch set (via %s).')
UNSET = object()  # Sentinel for unset config values.


def check_output(*args, **kwargs):
    """Run a command on the operation system.

    If the command fails a :class:`~subprocess.CalledProcessError`
    will occur. However, if you would like to silently ignore this
    error, pass the ``ignore_err`` flag::

      >>> print(check_output('false', ignore_err=True))
      None

    :type args: tuple
    :param args: Arguments to pass to ``subprocess.check_output``.

    :type kwargs: dict
    :param kwargs: Keyword arguments for this helper. Currently the
                   only accepted keyword argument is ``ignore_err`.

    :rtype: str
    :returns: The raw STDOUT from the command (converted from bytes
              if necessary).
    :raises TypeError: if any unrecognized keyword arguments are used.
    :raises CalledProcessError:
        If ``ignore_err`` is not :data:`True` and the system call fails.
    """
    ignore_err = kwargs.pop('ignore_err', False)
    if kwargs:
        raise TypeError('Got unexpected keyword argument(s)',
                        list(kwargs.keys()))

    try:
        kwargs = {}
        if ignore_err:
            kwargs['stderr'] = subprocess.PIPE  # Swallow stderr.
        cmd_output = subprocess.check_output(args, **kwargs)
        # On Python 3, this returns bytes (from STDOUT), so we
        # convert to a string.
        cmd_output_str = cmd_output.decode('utf-8')
        # Also strip the output since it usually has a trailing newline.
        return cmd_output_str.strip()
    except subprocess.CalledProcessError:
        if ignore_err:
            return
        else:
            raise


def pr_from_commit(merge_subject):
    """Get pull request ID from a commit message.

    .. note::

        This assumes we know the commit is a merge commit.

    :type merge_subject: str
    :param merge_subject: The subject of a merge commit.

    :rtype: int
    :returns: The PR ID extracted from the commit subject. If no integer
              can be uniquely extracted, returns :data:`None`.
    """
    matches = _PR_ID_REGEX.findall(merge_subject)
    if len(matches) == 1:
        # NOTE: We don't need to catch a ValueError since the regex
        #       guarantees the match will be all digits.
        return int(matches[0])


def _in_ci(env_var):
    """Detect if we are running in the target CI system.

    Assumes the only valid environment variable value is ``true``.

    :type env_var: str
    :param env_var: The environment variable which holds the status.

    :rtype: bool
    :returns: Flag indicating if we are running in the target CI system.
    """
    return os.getenv(env_var) == 'true'


def _ci_branch(env_var):
    """Get the current branch of CI build.

    :type env_var: str
    :param env_var: The environment variable which holds the branch.

    :rtype: str
    :returns: The name of the branch the current build is for / associated
              with. (May indicate the active branch or the base branch of
              a pull request.)
    :raises EnvironmentError: if the environment variable
                              isn't set during the build.
    """
    try:
        return os.environ[env_var]
    except KeyError as exc:
        msg = _BRANCH_ERR_TEMPLATE % (env_var,)
        raise EnvironmentError(exc, msg)


class Config(object):
    """Base class for caching CI configuration objects."""

    # Default instance attributes.
    _active = UNSET
    _branch = UNSET
    # Class attributes.
    _active_env_var = None
    _branch_env_var = None

    # pylint: disable=missing-returns-doc
    @property
    def active(self):
        """Indicates if currently running in the target CI system.

        :rtype: bool
        """
        if self._active is UNSET:
            self._active = _in_ci(self._active_env_var)
        return self._active

    @property
    def branch(self):
        """Indicates the current branch in the target CI system.

        This may indicate the active branch or the base branch of a
        pull request.

        :rtype: bool
        """
        if self._branch is UNSET:
            self._branch = _ci_branch(self._branch_env_var)
        return self._branch
    # pylint: enable=missing-returns-doc
