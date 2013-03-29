.. _howto:

How To Do Some Common Tasks
===========================

.. contents::
   :depth: 1
   :local:

Create a new Product Version for an existing Product
----------------------------------------------------

Situation
^^^^^^^^^
You have an existing Product, Version 1.0 along with
test cases, suites, etc.  Now you want to start testing version 2.0 of
that same product.  See :ref:`Product Versions <product-versions>` for more info
on the fields in that screen.

Steps
^^^^^
See Tutorial: :ref:`New Version<new-product-version>`


Fill in test cases missing from one Product Version into another
----------------------------------------------------------------

Situation
^^^^^^^^^
You have a 1.0 version of your product, and you created a 2.0
version as well.  Then later, you added some new test cases to 1.0 and want to
make sure those get included for testing in 2.0.

There are two situation variants, with different solutions:

    #. You only have a couple cases you want ported to 2.0.  And/or you have
       some cases in 1.0 that you do *not* want ported to 2.0.
    #. You have *lots* of new cases in 1.0 and want them all ported to 2.0.

Steps for solution 1
^^^^^^^^^^^^^^^^^^^^
    #. navigate to ``Manage | Cases``
    #. filter as appropriate to find the cases you want to port over to 2.0
    #. edit one of the cases
    #. In the upper right corner of the edit page, find the drop-down beneath
       the ``select environments`` button that shows the current version 1.0 of
       the test case.
    #. as you hover your mouse over the 1.0 version, the field will drop-down
       and you'll see an option that says: ``+ 2.0 (add this version)``
    #. Select that option
    #. click ``save test case``
    #. edit the next test case to port and repeat the steps to add the 2.0
       version.

Result
^^^^^^
You will see new 2.0 versions of each test case you edited.


Steps for solution 2
^^^^^^^^^^^^^^^^^^^^
    #. navigate to ``Manage | Versions``
    #. edit your 2.0 (destination) version.  **Note:** You can fill cases from
       2.0 back to 1.0, if you like, too.  Just edit the version that is your
       destination.
    #. set the ``Fill Cases From`` field to the product version to fill from.
    #. click ``save productversion``

Result
^^^^^^
All test cases in 1.0 now have a 2.0 version.  If a 2.0 version already existed
for a case, it will NOT replace it.


Migrate a test run to a new Product Version
-------------------------------------------

Situation
^^^^^^^^^
You have an existing Product, Version 1.0 along with
test cases, suites, runs, etc.  You created version 2.0 of the product and
want to run some of the same test runs against from 1.0 against 2.0.  You
will need to clone the 1.0 test runs to 2.0 and update them.

Steps
^^^^^
See Tutorial: :ref:`Migrate Runs<migrate-runs>`


Get a link to a result of a test just after submitting it
---------------------------------------------------------

Situation
^^^^^^^^^
You are executing a test run and find a bug.  You want to submit the bug, and
then provide a link to the result in your bug report.  Or perhaps you just want
to email that link to someone.

Steps for solution 1
^^^^^^^^^^^^^^^^^^^^
    #. run the test run
    #. mark the case with the result you found
    #. If, for example, the case was marked "Failed," then click the red button that says:
        * |case_result|

Result
^^^^^^
You are taken to the result for that test case.  You will also see any result
that other users have submitted for the same case in that environment.

.. |case_result| image:: img/case_result.png
    :height: 40px


