Cycles, Runs, and Results
=========================


.. _test-cycles:

Test Cycles
-----------

A **Test Cycle** is simply a container for :ref:`test runs <test-runs>`; its
meaning will depend on your project's workflow. For instance, it might
correspond to a release cycle. It has a *name*, a *start date*, an *end date*,
and a *product* and *product version*. It also has a *status*: either "draft",
"active", or "disabled". A test cycle must be marked "active" before any of its
member runs can be made active, and when a test cycle is disabled all member
runs are disabled as well.


.. _test-runs:

Test Runs
---------

A **Test Run** consists of a set of :ref:`test case <test-cases>` versions that
can be assigned to a tester for execution (or that a tester can assign to
themselves and execute) in a particular :ref:`environment <environments>` or
set of environments.

It is part of a :ref:`test cycle <test-cycles>` and inherits the *product
version* of the cycle. It has its own *name*, *status*, *start date*, and *end
date*, as well as a list of included :ref:`test suites <test-suites>`.

A test run must be switched to *active* status before it can be executed by
testers. When a test run is made active, the included test cases and their
versions are locked in for the life of that test run. For every included *test
suite*, the latest active version of each test case in that suite which is
marked as applicable to a product version less than or equal to the *product
version* of the run is included in the test run.

For instance, assume we have a product "Firefox" in the system with versions 8,
9, and 10, and we have a test run for version 9. When this test run is
activated, the test suite "Core" is included in it, and has a test case "Can
visit a web page" in it. That test case has versions 1, 2, and 3. Versions 1
and 2 are marked as for Firefox 8+, and version 3 is marked as for Firefox 10+.

Version 3 is the latest version of the test case, but cannot be included
because the test run is for Firefox 9, and version 3 only applies to Firefox
10+. So version 2 of the test case is included in the run, since it is the
latest version that applies to the correct version of the product.

An active test run can be disabled, which halts all execution of tests in that
run until it is made active again.


.. _test-results:

Test Results
------------

A **Test Result** stores the results of a single execution of one :ref:`test
case<test-cases>` from a :ref:`test run<test-runs>`, in a particular
:ref:`environment<environments>`, by a particular *tester*.

A result has a *status*, which can be any of **assigned** (the test
case/environment is assigned to this tester, but hasn't been run yet),
**started** (the tester has started executing the test, but hasn't yet reported
the result), **passed**, **failed**, or **invalidated** (the test case steps
were incorrect, did not apply, or the tester couldn't understand them).

The result also tracks the duration of execution (datetime *started* and
*completed*), as well as an optional *comment* from the tester.

A passed/failed/invalidated result can also be recorded for each individual
step in the test case, allowing the tester to specify precisely which step(s)
failed or were invalid. A failed step can have a *bug URL* associated with it.
