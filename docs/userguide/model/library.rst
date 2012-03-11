Test Cases and Suites
=====================

.. _test-cases:

Test Cases
----------

A **Test Case** is a named set of steps for testing a single feature or
characteristic of the system under test. Test cases are associated with a
:ref:`product <products>`, and can have one version per :ref:`product
version<product-versions>`. They can be organized via :ref:`suites
<test-suites>` and/or :ref:`tags<tags>`, and can have file
:ref:`attachments<attachments>`. Preconditions, assumptions, and other
preliminary information can be provided in the case's *description*. A test
case can have any number of steps; each step has an *instruction* and an
*expected result*.


.. _test-suites:

Test Suites
-----------

A **Test Suite** is a named collection of test cases that can be included in a
:ref:`test run<test-runs>`.


.. _tags:

Tags
----

A **Tag** can be associated with one or more :ref:`test cases<test-cases>` as a
way to organize and filter them on any number of axes.

By default, tags are :ref:`product<products>`-specific; global tags can also be
created and managed via the tag management UI.


.. _attachments:

Attachments
-----------

A :ref:`test case<test-cases>` can have any number of file attachments: these
will be made available for download by testers when the test case is executed.
