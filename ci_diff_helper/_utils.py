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

import re
import subprocess


_PR_ID_REGEX = re.compile(r'#(\d+)')
UNSET = object()  # Sentinel for unset config values.


def check_output(*args, **kwargs):
    """Run a command on the operation system.

    If the command fails a :class:`~subprocess.CalledProcessError`
    will occur. However, if you would like to silently ignore this
    error, pass the ``ignore_err`` flag::

      >>> print(check_output('false', ignore_err=True))
      None

    Args:
        args (tuple): Arguments to pass to ``subprocess.check_output``.
        kwargs (dict): Keyword arguments for this helper. Currently the
            only accepted keyword argument is ``ignore_err`.

    Returns:
        str: The raw STDOUT from the command (converted from bytes
            if necessary).

    Raises:
        TypeError: If any unrecognized keyword arguments are used.
        CalledProcessError: If ``ignore_err`` is not :data:`True` and
            the system call fails.
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

    Args:
        merge_subject (str): The subject of a merge commit.

    Returns:
        int: The PR ID extracted from the commit subject. If no integer
            can be uniquely extracted, returns :data:`None`.
    """
    matches = _PR_ID_REGEX.findall(merge_subject)
    if len(matches) == 1:
        # NOTE: We don't need to catch a ValueError since the regex
        #       guarantees the match will be all digits.
        return int(matches[0])
