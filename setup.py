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

import os

from setuptools import find_packages
from setuptools import setup


PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(PACKAGE_ROOT, 'README.rst')) as file_obj:
    README = file_obj.read()

REQUIREMENTS = (
    'enum34',
    'requests',
    'six >= 1.9.0',
)
DESCRIPTION = 'Diff Helper for Continuous Integration (CI) Services'


setup(
    name='ci-diff-helper',
    version='0.0.2',
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
