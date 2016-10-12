CI Diff Helper
==============

    Diff Helper for Continuous Integration (CI) Services

|pypi| |build| |appveyor| |coverage| |versions| |docs|

For an open source project, running unit tests, system tests, torture tests,
fuzz tests, integration tests, code quality checks, etc. can quickly become
a large task.

In order to limit the amount of time and resources that these jobs require,
this tool provides a way to determine which files have changed and provides
a Python API for these changes. In addition, this library provides the
corresponding commit SHA (or other artifact) that is used as the diffbase.

The library supports (planned)

* Continuous Integration Services

  * `Travis CI`_
  * `AppVeyor`_

* Verson Control Systems

  * `git`_

* Project Hosting Sites (planned)

  * `GitHub`_

.. _Travis CI: https://travis-ci.com/
.. _AppVeyor: https://www.appveyor.com/
.. _git: https://git-scm.com/
.. _GitHub: https://github.com/

Install
-------

::

    $ pip install --upgrade ci-diff-helper

See It In Action
----------------

The ``test-app`` `branch`_ is set up to run in Travis
every time a change is made. Check out the `latest builds`_
in ``test-app`` to see the computed values at work.

For example, in a `PR build`_::

        active: True
          base: 'test-app'
        branch: 'test-app'
    event_type: <TravisEventType.pull_request: 'pull_request'>
           ...

and in a `push build`_::

        active: True
          base: u'cbe48c9ae38e3ee4a4b6f6696e071fa9a1b9dabb'
        branch: 'test-app'
    event_type: <TravisEventType.push: 'push'>
           ...

.. _branch: https://github.com/dhermes/ci-diff-helper/tree/test-app
.. _latest builds: https://travis-ci.org/dhermes/ci-diff-helper/branches
.. _PR build: https://travis-ci.org/dhermes/ci-diff-helper/builds/166910963
.. _push build: https://travis-ci.org/dhermes/ci-diff-helper/builds/166927258

License
-------

Apache 2.0 - See `LICENSE`_ for more information.

.. _LICENSE: https://github.com/dhermes/ci-diff-helper/blob/master/LICENSE

.. |build| image:: https://travis-ci.org/dhermes/ci-diff-helper.svg?branch=master
   :target: https://travis-ci.org/dhermes/ci-diff-helper
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
