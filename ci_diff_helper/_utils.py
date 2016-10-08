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

import subprocess


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
