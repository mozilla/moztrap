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
one iteration prior to release of that version. For this purpose, you may
want to make a Test Run that is a :ref:`Series <test-run-series>`.

The test case steps executed in test runs may be different for each Product
Version, as the Product itself evolves. See :ref:`Test Cases <test-cases>` for
more info on how test case versions relate to Product Versions.

An active test run can be disabled, which halts all execution of tests in that
run until it is made active again.

.. _test-run-series:

Test Run Series
~~~~~~~~~~~~~~~

A **Test Run** can be marked as a series of runs, by checking the "Is Series"
box.  You define the run just as you would any other run by specifying the
:ref:`product <products>` version and suites.  The difference is that, this
**Series** run is now just a template used for each build of your product to
be tested.

When you execute a run that is a series, you will be prompted for your
environment options, like always.  But you will also be asked for a build id.
If there is already a member of this series that has that build id, then you
will begin testing it.  If, however, no one has run this series on that build
yet, then a new member of the series will be created and you will start
testing it.  The name of this new member of the series will contain the build
id you specified.  For instance, with a run series called "Smoketest,"
specifying a build of "Alpha1" will result in a new member of the series
named "Smoketest - Build: Alpha1" with distinct results from any other member
in the series.

When viewing the list of runs in the manage or results lists, you can then
filter to see only runs that belong to a specific series.

Cloning Test Runs
~~~~~~~~~~~~~~~~~

If you have a Test Run that you would like to apply to a different Product
Version, you must clone the existing Test Run, then edit the new clone while it
is still in draft mode. Once your changes are made, you can activate the new
run to use it.

Sharing links to Runs
~~~~~~~~~~~~~~~~~~~~~

Often you might create a run or run series and want to send a link to your
testers asking them to execute it in their own testing environment.  This also
works great for a run :ref:`series <test-run-series>`.  To get this link,
expand the details for your run in the manage runs area.  You'll see a big
green button saying **run tests in <yourrunname>**.  Just right-click and copy
that url location to share.

.. _test-run-edit-fields:

Run Edit Fields
^^^^^^^^^^^^^^^^

* **Product Version** - The product version of this test run.  Runs are
  specific to a version of a product, not just the product in general.
* **Name** - The summary name for the run.  When testing a product that has
  build numbers, you may choose to include the build number in the name to
  distinguish it from other runs against the same version of the product.
  Dates in the name are another good way to distinguish runs from one another.
* **Series** - (optional) Whether or not this run is a
  :ref:`series <test-run-series>` of runs.  Default to True.
* **Description** - (optional) Any description for the run.  This description
  is displayed in the management details area as well as at the top of the
  page while executing a run.  Description text supports Markdown_ syntax which
  could include links to things like entering a new bug in one or more areas or
  extra info for your testers.
* **Start** - The first date that the run can be executed
* **End** - The date the run expires.  A run cannot be executed after its
  end date.
* **Available Suites** - All the suites that apply to the specified Product
  Version.  This field is filterable.
* **Selected Suites** - The suites from which to gather test cases for this
  run.  When the run is activated, only suites and cases that were active at
  that time will be included in the run.  This field is not filterable.

.. _Markdown: http://daringfireball.net/projects/markdown/syntax


Refreshing a Run
----------------

.. _test-run-refresh:

When a test run is made active, it will take a snapshot of active
suites and cases at that time. If cases and suites are added, removed or had
their active status changed since the run was made active, the run won't
appear changed to testers.  This is because once a test run is activated, it
is considered a *unit of work* that you may not want to alter while testers
are executing the run.

If, however, you want to refresh the run with the new list of active cases
and suites, then you can click the *refresh* button in the management area
next to your run.  This won't affect existing results unless you have removed
a case from one of the run's suites.

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
