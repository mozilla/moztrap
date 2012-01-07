Test Cases and Suites
=====================

Test cases and test suites represent the long-term


.. _test-cases:

Test Cases
----------

A **Test Case** is a named set of steps for testing a single feature or
characteristic of the system under test. Test cases are associated with a
`product <products>`_ and *product version*. They can be organized via
:ref:`suites <test-suites>` and/or *tags*, and can have file
*attachments*. Preconditions, assumptions, and other preliminary information
can be provided in the case's *description*. A test case can have any number of
steps; each step has an *instruction* and an *expected result*.

Test cases are versioned linearly; all previous versions are saved (and may
also still be in use in earlier test runs). Minor edits can be made to any
version in-place; major edits to any version result in the creation of a new
latest version; there is no version branching. In other words, saving major
edits to a non-latest version effectively supersedes any changes in existing
later versions.


.. _test-suites:

Test Suites
-----------

A **Test Suite** is a named collection of test cases that can be included in a
test run. Test suites do not include specific versions of cases (or to put it
differently, they always implicitly include the latest version of each
case). When a test suite is added to a test run, the latest version of each
case in the suite will be included in that run.
