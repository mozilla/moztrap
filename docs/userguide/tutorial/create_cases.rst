.. _tutorial-create-tests:

MozTrap Tutorial, part 2
========================

In this section, we discuss creating test cases and organizing them into
suites.

Create test Suites
------------------

Test Suites are collections of test cases.  A test case can belong to more
than one suite, if need be.

Let's write some tests to cover two areas of the **SpeckDetector**.  It should
detect specks of sand and specks of pollen.  And you should also be able to
update your SpeckDetector's firmware.

Steps
^^^^^
    #. Navigate to ``manage | suites``.
    #. Click ``create a test suite``.
    #. Set your product to ``SpeckDetector``.
    #. Set name to ``Specks``.
    #. Enter a description that includes Markdown_ syntax::

        PRECONDITIONS
        =============
        * Must have some specks

        LINKS
        =====
        * [Specks of Life](http://example.com/)

    #. You won't have any available cases yet, so skip that and just
       click ``save suite``.
    #. Repeat these steps for a suite but name it ``Firmware``.

Create test Cases
-----------------

Now we need to create some test cases for those suites.

Steps
^^^^^
    #. Navigate to ``manage | cases``.
    #. Click ``create a test case``.
    #. Set your product to ``SpeckDetector``.
    #. Set version to ``1.0``.
    #. Set suite to ``Specks``.
    #. :ref:`ID Prefix<test-case-edit-fields>` is optional, skip it for now.
    #. Set name to ``Detect a pollen speck``.
    #. For ``instruction`` 1, enter::

        hold detector held away from pollen

    #. For ``expected`` 1, enter::

        no detection lights

    #. Tab to ``instruction`` 2, enter::

        hold detector above a pollen speck

    #. Tab to ``expected`` 2, enter::

        detector lights up word "pollen"

    #. Click ``save test case``.


That's one down.  Whew!  OK, now create another test case for the ``firmware``
suite with steps like this:

    #. Name: ``update firmware``.
    #. For ``instruction`` 1, enter::

        navigate to firmware update screen and select "update"

    #. For ``expected`` 1, enter::

        see "a firmware update is available"

    #. Tab to ``instruction`` 2, enter::

        click "apply update"

    #. Tab to ``expected`` 2, enter::

        firmware value should say the new version


Great!  You're done with your cases!

.. _Markdown: http://daringfireball.net/projects/markdown/syntax

