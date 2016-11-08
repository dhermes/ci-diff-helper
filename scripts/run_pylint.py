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

"""Custom script to run Pylint on ci-diff-helper.

This runs pylint as a script via subprocess in two different
subprocesses. The first lints the production/library code
using the default rc file (PRODUCTION_RC). The second lints the
test code using an rc file (TEST_RC) which allows more style
violations (hence it has a reduced number of style checks).
"""

from __future__ import print_function

import collections
import copy
import io
import os
import subprocess
import sys

import six

import ci_diff_helper


_SCRIPTS_DIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTION_RC = os.path.join(_SCRIPTS_DIR, 'pylintrc_production')
TEST_RC = os.path.join(_SCRIPTS_DIR, 'pylintrc_test')

_ERROR_TEMPLATE = 'Pylint failed on {} with status {:d}.'
_SKIP_TEMPLATE = 'Skipping {}, no files to lint.'

_PRODUCTION_RC_ADDITIONS = {
    'MESSAGES CONTROL': {
        'disable': ['I'],
    },
}
_PRODUCTION_RC_REPLACEMENTS = {
    'MASTER': {
        'load-plugins': 'pylint.extensions.check_docs',
        'jobs': '4',
    },
    'DESIGN': {
        'max-attributes': '10',
    },
    'REPORTS': {
        'reports': 'no',
    },
    'FORMAT': {
        'max-line-length': '80',
        'no-space-check': '',
        'expected-line-ending-format': 'LF',
    },
}
_TEST_RC_ADDITIONS = copy.deepcopy(_PRODUCTION_RC_ADDITIONS)
_TEST_RC_ADDITIONS['MESSAGES CONTROL']['disable'].extend([
    'missing-docstring',
    'protected-access',
    'similarities',
    'too-many-public-methods',
])
_TEST_RC_REPLACEMENTS = copy.deepcopy(_PRODUCTION_RC_REPLACEMENTS)
_TEST_RC_REPLACEMENTS.setdefault('BASIC', {})
_TEST_RC_REPLACEMENTS['BASIC']['class-rgx'] = (
    '([A-Z_][a-zA-Z0-9]+|Test_.*)$')

_ROOT_DIR = os.path.abspath(os.path.join(_SCRIPTS_DIR, '..'))
IGNORED_FILES = (
    os.path.join(_ROOT_DIR, 'docs', 'conf.py'),
)


def get_default_config():
    """Get the default Pylint configuration.

    Returns:
        str: The default Pylint configuration.
    """
    # Swallow STDERR if it says
    # "No config file found, using default configuration"
    result = subprocess.check_output(['pylint', '--generate-rcfile'],
                                     stderr=subprocess.PIPE)
    # On Python 3, this returns bytes (from STDOUT), so we
    # convert to a string.
    return result.decode('utf-8')


def read_config(contents):
    """Reads pylintrc config into native ConfigParser object.

    Args:
        contents (str): The contents of the file containing the INI config.

    Returns:
        ConfigParser.ConfigParser: The parsed configuration.
    """
    file_obj = io.StringIO(contents)
    config = six.moves.configparser.ConfigParser()
    config.readfp(file_obj)
    return config


def _transform_opt(opt_val):
    """Transform a config option value to a string.

    If already a string, do nothing. If an iterable, then
    combine into a string by joining on ",".

    Args:
        opt_val (Union[str, list]): A config option's value.

    Returns:
        str: The option value converted to a string.
    """
    if isinstance(opt_val, (list, tuple)):
        return ','.join(opt_val)
    else:
        return opt_val


def make_rc(base_cfg, target_filename,
            additions=None, replacements=None):
    """Combines a base rc and additions into single file.

    Args:
        base_cfg (ConfigParser.ConfigParser): The configuration we
            are merging into.
        target_filename (str): The filename where the new configuration
            will be saved.
        additions (Optional[dict]): The values added to the configuration.
        replacements (Optional[dict]): The wholesale replacements for the
            new configuration.

    Raises:
        KeyError: If one of the additions or replacements does not
            already exist in the current config.
    """
    # Set-up the mutable default values.
    if additions is None:
        additions = {}
    if replacements is None:
        replacements = {}

    # Create fresh config, which must extend the base one.
    new_cfg = six.moves.configparser.ConfigParser()
    # pylint: disable=protected-access
    new_cfg._sections = copy.deepcopy(base_cfg._sections)
    new_sections = new_cfg._sections
    # pylint: enable=protected-access

    for section, opts in additions.items():
        curr_section = new_sections.setdefault(
            section, collections.OrderedDict())
        for opt, opt_val in opts.items():
            curr_val = curr_section.get(opt)
            if curr_val is None:
                raise KeyError('Expected to be adding to existing option.')
            curr_val = curr_val.rstrip(',')
            opt_val = _transform_opt(opt_val)
            curr_section[opt] = '{}, {}'.format(curr_val, opt_val)

    for section, opts in replacements.items():
        curr_section = new_sections.setdefault(
            section, collections.OrderedDict())
        for opt, opt_val in opts.items():
            curr_val = curr_section.get(opt)
            if curr_val is None:
                raise KeyError('Expected to be replacing existing option.')
            opt_val = _transform_opt(opt_val)
            curr_section[opt] = '{}'.format(opt_val)

    with open(target_filename, 'w') as file_obj:
        new_cfg.write(file_obj)


def valid_filename(filename):
    """Checks if a file is a valid Python file.

    Args:
        filename (str): The name of a source file.

    Returns:
        bool: Flag indicating if the file is valid.
    """
    if filename in IGNORED_FILES:
        return False
    if not os.path.exists(filename):
        return False
    _, ext = os.path.splitext(filename)
    return ext == '.py'


def is_test_filename(filename):
    """Checks if the file is a test file.

    Args:
        filename (str): The name of a source file.

    Returns:
        bool: Boolean indicating if ``filename`` is a test file.
    """
    return 'test' in filename


def get_python_files(all_files=None):
    """Gets a list of all Python files in the repository.

    Separates the files based on test or production code according
    to :func:`is_test_filename`.

    Args:
        all_files (Optional[list]): A list of all files to consider.

    Returns:
        Tuple[list, list]: A tuple containing two lists. The first list
            contains all production files, the next all test files.
    """
    if all_files is None:
        all_files = ci_diff_helper.get_checked_in_files()

    production_files = []
    test_files = []
    for filename in all_files:
        if not valid_filename(filename):
            continue
        if is_test_filename(filename):
            test_files.append(filename)
        else:
            production_files.append(filename)

    return production_files, test_files


def lint_fileset(filenames, rc_filename, description):
    """Lints a group of files using a given rcfile.

    Args:
        filenames (list): A list of files to be linted.
        rc_filename (str): The name of the Pylint config RC file.
        description (str): A description of the files and configuration
            currently being run.
    """
    if filenames:
        pylint_shell_command = ['pylint', '--rcfile', rc_filename]
        pylint_shell_command.extend(filenames)
        status_code = subprocess.call(pylint_shell_command)
        if status_code != 0:
            error_message = _ERROR_TEMPLATE.format(
                description, status_code)
            print(error_message, file=sys.stderr)
            sys.exit(status_code)
    else:
        print(_SKIP_TEMPLATE.format(description))


def main(all_files=None):
    """Script entry point. Lints both sets of files.

    Args:
        all_files (Optional[list]): A list of all files to consider.
    """
    default_config = read_config(get_default_config())
    make_rc(default_config, PRODUCTION_RC,
            additions=_PRODUCTION_RC_ADDITIONS,
            replacements=_PRODUCTION_RC_REPLACEMENTS)
    make_rc(default_config, TEST_RC,
            additions=_TEST_RC_ADDITIONS,
            replacements=_TEST_RC_REPLACEMENTS)
    production_files, test_files = get_python_files(all_files=all_files)
    lint_fileset(production_files, PRODUCTION_RC, 'Library')
    lint_fileset(test_files, TEST_RC, 'Test')


if __name__ == '__main__':
    main()
