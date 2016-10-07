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

"""Set of utilities for dealing with Travis CI.

Since Travis only works with GitHub, the commands in this module
are GitHub and ``git`` centric.

This module uses a selection of environment variables to detect
the state of Travis configuration. Among them are:

* ``TRAVIS``: to indicate if running in ``TRAVIS``
* ``TRAVIS_PULL_REQUEST``: to indicate which pull request we are in
  (this is an integer) or to indicate it is a push build
* ``TRAVIS_BRANCH``: to indicate the branch that was pushed (for a
  "push" build) or the branch that a pull request is against

For more details, see the `Travis env docs`_.

.. _Travis env docs: https://docs.travis-ci.com/user/\
                     environment-variables#Default-Environment-Variables
"""

import os


_IN_TRAVIS_ENV = 'TRAVIS'


def _in_travis():
    """Detect if we are running in Travis.

    :rtype: bool
    :returns: Flag indicating if we are running on Travis.
    """
    return os.getenv(_IN_TRAVIS_ENV) == 'true'


class Travis(object):
    """Represent Travis state and cache return values."""

    _active = None

    @property
    def active(self):
        """Indicates if currently running in Travis.

        :rtype: bool
        """
        if self._active is None:
            self._active = _in_travis()
        return self._active
