Diff Helper for Continuous Integration (CI) Services
====================================================

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
