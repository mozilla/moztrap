Runs and Results
================


.. _test-runs:

Test Runs
---------

A **Test Run** consists of a set of :ref:`test case <test-cases>` versions that
can be assigned to a tester for execution (or that a tester can assign to
themselves and execute) in a particular :ref:`environment <environments>` or
set of environments.

A test run is for a specific :ref:`product <products>` version. It has its own
*name*, *status*, *start date*, and *end date*, as well as a list of included
:ref:`test suites <test-suites>`. A test run must be switched to *active*
status before it can be executed by testers.

A Test Run applies to a Product and a Product Version. Usually, a product has
had several iterations (or builds) prior to the release of a final
Version. Therefore, a Test Run is a single execution pass over a specific
iteration of that Product Version. And your product will likely have more than
one iteration prior to release of that version. Therefore, you may choose to
name your test runs after the build they are testing like Build 23, Build 24,
etc. Once your product goes Alpha or Beta, you may choose to name your test
runs that way: "Alpha 1, Build 86," "Alpha 1, Build 87," etc.

The test case steps executed in test runs may be different for each Product
Version, as the Product itself evolves. See :ref:`Test Cases <test-cases>` for
more info on how test case versions relate to Product Versions.

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
