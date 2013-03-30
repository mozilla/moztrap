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
    #. navigate to ``manage | suites``
    #. click ``create a test suite``
    #. set your product to ``SpeckDetector``
    #. set name to ``Specks``
    #. enter a description that includes Markdown_ syntax::

        PRECONDITIONS
        =============
        * Must have some specks

        LINKS
        =====
        * [Specks of Life](http://example.com/)

    #. you won't have any available cases yet, so skip that and just
       click ``save suite``
    #. repeat these steps for a suite but name it ``Firmware``

Create test Cases
-----------------

Now we need to create some test cases for those suites.

Steps
^^^^^
    #. navigate to ``manage | cases``
    #. click ``create a test case``
    #. set your product to ``SpeckDetector``
    #. set version to ``1.0``
    #. set suite to ``Specks``
    #. :ref:`ID Prefix<test-case-edit-fields>` is optional, skip it for now
    #. set name to ``Detect a pollen speck``
    #. for ``instruction`` 1, enter::

        hold detector held away from pollen

    #. for ``expected`` 1, enter::

        no detection lights

    #. tab to ``instruction`` 2, enter::

        hold detector above a pollen speck

    #. tab to ``expected`` 2, enter::

        detector lights up word "pollen"

    #. click ``save test case``


That's one down.  Whew!  OK, now create another test case for the ``firmware``
suite with steps like this:

    #. name: ``update firmware``
    #. for ``instruction`` 1, enter::

        navigate to firmware update screen and select "update"

    #. for ``expected`` 1, enter::

        see "a firmware update is available"

    #. tab to ``instruction`` 2, enter::

        click "apply update"

    #. tab to ``expected`` 2, enter::

        firmware value should say the new version


Great!  You're done with your cases!

.. _Markdown: http://daringfireball.net/projects/markdown/syntax

