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

"""Custom script to run lint rules on ci-diff-helper."""

import ci_diff_helper
import pycodestyle_on_repo
import run_pylint


def main():
    """Script entry point.

    Runs Pylint and pycodestyle.
    """
    all_files = ci_diff_helper.get_checked_in_files()
    pycodestyle_on_repo.main(all_files=all_files)
    run_pylint.main(all_files=all_files)


if __name__ == '__main__':
    main()
