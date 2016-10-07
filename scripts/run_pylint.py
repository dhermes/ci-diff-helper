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
import ConfigParser
import copy
import io
import os
import subprocess
import sys

import ci_diff_helper


_SCRIPTS_DIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTION_RC = os.path.join(_SCRIPTS_DIR, 'pylintrc_production')
TEST_RC = os.path.join(_SCRIPTS_DIR, 'pylintrc_test')

_ERROR_TEMPLATE = 'Pylint failed on %s with status %d.'
_SKIP_TEMPLATE = 'Skipping %s, no files to lint.'

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

    :rtype: str
    :returns: The default Pylint configuration.
    :raises EnvironmentError: if the system call fails for some reason.
    """
    # NOTE: We uses subprocess.Popen instead of subprocess.check_output()
    #       so that we can also swallow STDERR.
    proc = subprocess.Popen(['pylint', '--generate-rcfile'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    status_code = proc.wait()
    if status_code != 0:
        raise EnvironmentError('Failed to generate Pylint RC file.')
    result = proc.stdout.read()
    # On Python 3, this returns bytes (from STDOUT), so we
    # convert to a string.
    return result.decode('utf-8')


def read_config(contents):
    """Reads pylintrc config onto native ConfigParser object.

    :type contents: str
    :param contents: The contents of the file containing the INI config.

    :rtype: :class:`ConfigParser.ConfigParser`
    :returns: The parsed configuration.
    """
    file_obj = io.StringIO(contents)
    config = ConfigParser.ConfigParser()
    config.readfp(file_obj)
    return config


def _transform_opt(opt_val):
    """Transform a config option value to a string.

    If already a string, do nothing. If an iterable, then
    combine into a string by joining on ",".

    :type opt_val: str or list
    :param opt_val: A config option's value.

    :rtype: str
    :returns: The option value converted to a string.
    """
    if isinstance(opt_val, (list, tuple)):
        return ','.join(opt_val)
    else:
        return opt_val


def make_rc(base_cfg, target_filename,
            additions=None, replacements=None):
    """Combines a base rc and additions into single file.

    :type base_cfg: :class:`ConfigParser.ConfigParser`
    :param base_cfg: The configuration we are merging into.

    :type target_filename: str
    :param target_filename: The filename where the new

    :type additions: dict
    :param additions: (Optional) The values added to the configuration.

    :type replacements: dict
    :param replacements: (Optional) The wholesale replacements for the
                         new configuration.

    :raises KeyError: if one of the additions or replacements does not
                      already exist in the current config.
    """
    # Set-up the mutable default values.
    if additions is None:
        additions = {}
    if replacements is None:
        replacements = {}

    # Create fresh config, which must extend the base one.
    new_cfg = ConfigParser.ConfigParser()
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
            curr_section[opt] = '%s, %s' % (curr_val, opt_val)

    for section, opts in replacements.items():
        curr_section = new_sections.setdefault(
            section, collections.OrderedDict())
        for opt, opt_val in opts.items():
            curr_val = curr_section.get(opt)
            if curr_val is None:
                raise KeyError('Expected to be replacing existing option.')
            opt_val = _transform_opt(opt_val)
            curr_section[opt] = '%s' % (opt_val,)

    with open(target_filename, 'w') as file_obj:
        new_cfg.write(file_obj)


def valid_filename(filename):
    """Checks if a file is a valid Python file.

    :type filename: str
    :param filename: The name of a source file.

    :rtype: bool
    :returns: Flag indicating if the file is valid.
    """
    if filename in IGNORED_FILES:
        return False
    if not os.path.exists(filename):
        return False
    _, ext = os.path.splitext(filename)
    return ext == '.py'


def is_test_filename(filename):
    """Checks if the file is a test file.

    :type filename: str
    :param filename: The name of a source file.

    :rtype: bool
    :returns: Boolean indicating if ``filename`` is a test file.
    """
    return 'test' in filename


def get_python_files(all_files=None):
    """Gets a list of all Python files in the repository.

    Separates the files based on test or production code according
    to :func:`is_test_filename`.

    :type all_files: list
    :param all_files: (Optional) A list of all files to consider.

    :rtype: tuple
    :returns: A tuple containing two lists. The first list
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

    :type filenames: list
    :param filenames: A list of files to be linted.

    :type rc_filename: str
    :param rc_filename: The name of the Pylint config RC file.

    :type description: str
    :param description: A description of the files and configuration
                        currently being run.
    """
    if filenames:
        pylint_shell_command = ['pylint', '--rcfile', rc_filename]
        pylint_shell_command.extend(filenames)
        status_code = subprocess.call(pylint_shell_command)
        if status_code != 0:
            error_message = _ERROR_TEMPLATE % (description,
                                               status_code)
            print(error_message, file=sys.stderr)
            sys.exit(status_code)
    else:
        print(_SKIP_TEMPLATE % (description,))


def main(all_files=None):
    """Script entry point. Lints both sets of files.

    :type all_files: list
    :param all_files: (Optional) A list of all files to consider.
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
