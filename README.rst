CI Diff Helper
==============

    Diff Helper for Continuous Integration (CI) Services

|pypi| |coverage| |versions| |docs|

For an open source project, running unit tests, system tests, torture tests,
fuzz tests, integration tests, code quality checks, etc. can quickly become
a large task.

In order to limit the amount of time and resources that these jobs require,
this tool provides a way to determine which files have changed and provides
a Python API for these changes. In addition, this library provides the
corresponding commit SHA (or other artifact) that is used as the diffbase.

The library supports (planned)

* Continuous Integration Services

  * `Travis CI`_ |build|
  * `AppVeyor`_ |appveyor|
  * `CircleCI`_ |build-circ|

* Verson Control Systems

  * `git`_

* Project Hosting Sites

  * `GitHub`_

.. _Travis CI: https://travis-ci.com/
.. _AppVeyor: https://www.appveyor.com/
.. _CircleCI: https://circleci.com/
.. _git: https://git-scm.com/
.. _GitHub: https://github.com/

Install
-------

.. code-block:: console

    $ pip install --upgrade ci-diff-helper

See It In Action
----------------

The ``test-app`` `branch`_ is set up to run every time a change is made.
Check out the `latest Travis builds`_ in ``test-app``, the
`latest CircleCI builds`_ and the `latest AppVeyor builds`_
to see the computed values at work.

For example, in a `Travis PR build`_::

        active: True
          base: 'test-app'
        branch: 'test-app'
    event_type: <TravisEventType.pull_request: 'pull_request'>
           ...

and in a `Travis push build`_::

    Config object: <Travis (active=True)>
    ----------------------------------------
                    active: True
                      base: u'da0c87dcc580b8322a5c6d683a1bcd30d3873387'
                    branch: 'test-app'
                event_type: <TravisEventType.push: 'push'>
                     in_pr: False
                  is_merge: False
                 merged_pr: None
                        pr: None
                      slug: 'dhermes/ci-diff-helper'
                       tag: None
                       ...

A `CircleCI push build`_::

    Config object: <CircleCI (active=True)>
    ----------------------------------------
                    active: True
                    branch: 'test-app'
                  is_merge: False
                       tag: None
                       ...

An `AppVeyor push build`_::

    Config object: <AppVeyor (active=True)>
    ----------------------------------------
                    active: True
                    branch: 'test-app'
                  is_merge: False
                  provider: <AppVeyorRepoProvider.github: 'github'>
                       tag: None
                       ...

.. _branch: https://github.com/dhermes/ci-diff-helper/tree/test-app
.. _latest Travis builds: https://travis-ci.org/dhermes/ci-diff-helper/branches
.. _latest CircleCI builds: https://circleci.com/gh/dhermes/ci-diff-helper/tree/test-app
.. _latest AppVeyor builds: https://ci.appveyor.com/project/dhermes/ci-diff-helper/history?branch=test-app
.. _Travis PR build: https://travis-ci.org/dhermes/ci-diff-helper/builds/166910963
.. _Travis push build: https://travis-ci.org/dhermes/ci-diff-helper/builds/174374853
.. _CircleCI push build: https://circleci.com/gh/dhermes/ci-diff-helper/45
.. _AppVeyor push build: https://ci.appveyor.com/project/dhermes/ci-diff-helper/build/1.0.136.test-app

License
-------

Apache 2.0 - See `LICENSE`_ for more information.

.. _LICENSE: https://github.com/dhermes/ci-diff-helper/blob/master/LICENSE

.. |build| image:: https://travis-ci.org/dhermes/ci-diff-helper.svg?branch=master
   :target: https://travis-ci.org/dhermes/ci-diff-helper
.. |build-circ| image:: https://circleci.com/gh/dhermes/ci-diff-helper.png?style=shield
   :target: https://circleci.com/gh/dhermes/ci-diff-helper
   :alt: CirleCI Build
.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/dhermes/ci-diff-helper?branch=master&svg=true
   :target: https://ci.appveyor.com/project/dhermes/ci-diff-helper
.. |coverage| image:: https://coveralls.io/repos/github/dhermes/ci-diff-helper/badge.svg?branch=master
   :target: https://coveralls.io/github/dhermes/ci-diff-helper?branch=master
.. |pypi| image:: https://img.shields.io/pypi/v/ci-diff-helper.svg
   :target: https://pypi.python.org/pypi/ci-diff-helper
.. |versions| image:: https://img.shields.io/pypi/pyversions/ci-diff-helper.svg
   :target: https://pypi.python.org/pypi/ci-diff-helper
.. |docs| image:: https://readthedocs.org/projects/ci-diff-helper/badge/?version=latest
   :target: http://ci-diff-helper.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
