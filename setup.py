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

"""Setup file for ci-diff-helper."""

import collections
import os

from setuptools import find_packages
from setuptools import setup


VERSION = '0.1.0'
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(PACKAGE_ROOT, 'README.rst')) as file_obj:
    README = file_obj.read()

# Remove PyPI and Python versions badges from README since this
# will show up on PyPI.
README = README.replace(
    '|pypi| |build| |appveyor| |coverage| |versions| |docs|',
    '|build| |appveyor| |coverage| |docs|')
BADGES_START = README.index('.. |build| image')
BADGES_TEXT = '\n' + README[BADGES_START:].strip()
# We know ``BADGES_TEXT`` starts with '\n.. |build' hence when we
# split on '\n .. |' to find each badge's info.
BADGES = collections.OrderedDict()
for line in BADGES_TEXT.split('\n.. |')[1:]:
    BADGE_NAME = line[:line.index('|')]
    BADGES[BADGE_NAME] = '.. |' + line
# Continue removing PyPI and Python versions badges.
BADGES.pop('pypi')
BADGES.pop('versions')
# Update the Travis CI badge.
BADGES['build'] = BADGES['build'].replace(
    'branch=master', 'tag=' + VERSION)
# Update the coveralls.io badge.
BADGES['coverage'] = BADGES['coverage'].replace(
    'branch=master', 'branch=' + VERSION)
# Update the docs badge.
BADGES['docs'] = BADGES['docs'].replace('latest', VERSION)
# Update the AppVeyor badge.
BADGES['appveyor'] = BADGES['appveyor'].replace(
    'branch=master', 'tag=' + VERSION)
# Update the README with the new tag content.
README = README[:BADGES_START] + '\n'.join(BADGES.values()) + '\n'

REQUIREMENTS = (
    'enum34',
    'requests',
    'six >= 1.9.0',
)
DESCRIPTION = 'Diff Helper for Continuous Integration (CI) Services'


setup(
    name='ci-diff-helper',
    version=VERSION,
    description=DESCRIPTION,
    author='Danny Hermes',
    author_email='daniel.j.hermes@gmail.com',
    long_description=README,
    scripts=(),
    url='https://github.com/dhermes/ci-diff-helper',
    packages=find_packages(),
    license='Apache 2.0',
    platforms='Posix; MacOS X; Windows',
    include_package_data=True,
    zip_safe=True,
    install_requires=REQUIREMENTS,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
    ),
)
