Running Tests
=============

.. _runtests:

To execute a :ref:`Test Run<test-runs>` select the **Run Tests** tab at the top
of MozTrap.  From here, select the :ref:`Product<products>`,
:ref:`Product Version<product-versions>` and :ref:`Run<test-runs>`.  Then you
will be prompted to enter the :ref:`environment<environments>` you are using
to test.

.. _result-statuses:

Result Statuses
---------------
* **passed** - All steps of the test matched the expected result.
* **failed** - One or more steps of the test did not match the expected result.
* **invalid** - The steps of the test were either incorrect, or unclear to the
                extent that it was not possible to determine if it passed or
                failed
* **skipped** - A test manager decided this test should not be run and should
                not count against the % complete.  Marking a test *skipped*
                only marks it for the specific environment it was skipped in.
* **blocked** - The test could not be run because the user was blocked from
                beginning the test.  For example, if the steps are to complete
                a purchase of something in their shopping cart, but the user
                can't even add items to the shopping cart, then the case could
                be considered blocked.

.. _marking-results:

Marking a result
----------------
Expand a case to see buttons to mark the test *passed, failed, skipped,
blocked or invalid*.
You can fail any specific step of a test case.  Marking a case invalid means
that the tester was not able to execute the test and it needs updating.


.. _other-results:

Results of others
-----------------
On the summary line of a test, an icon will appear if another tester has
already executed that test in the same environment.  If this icon shows, it
will display the status the other user gave it (passed, failed or invalid).
Hovering your mouse over the icon will display any comments the user made on
invalid or failed tests.  If you click this button, a new tab will open to show
you the specifics of all results given for this test.


.. _update-test:

Updating a test
---------------
Click the **Edit Case Details** in the test description to update the test
case.  This will take you to the edit page for the test case.  When you return
to the run page, you will need to refresh your page to see the updates.