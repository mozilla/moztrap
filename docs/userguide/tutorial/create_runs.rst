.. _tutorial-create-runs:

Moztrap Tutorial, part 3
========================

In this section, we use the pieces you've already built to create and activate
a test run that users can execute.


Create a Test Run
-----------------

Test Runs are made up of test suites and are specific to a version of your
product.  You may want to have several test runs.  One could be called
``smoke`` and another ``feature complete`` and yet another
``full functional tests``.  Or you could break them up into larger functional
areas like ``front-end`` and ``server``.

Let's create your first **SpeckDetector** test run.  It will contain all the
suites you have created so far.  Let's call this ``feature complete``.

Steps
^^^^^
    #. navigate to ``manage | runs``
    #. click ``create a test run``
    #. set your product version to ``SpeckDetector 1.0``
    #. set name to ``feature complete``
    #. enter a description that includes Markdown_ syntax.  This information
       will be displayed at the top of each page while running the tests::

        LINKS
        =====
        * [Specks of Life](http://example.com/)
        * [Bugzilla](http://bugzilla.mycompany.com)

    #. :ref:`series<test-run-series>` defaults to true.  We will want to run
       our tests against several ongoing builds of the **SpeckDetector**, so
       in our case we *will* create a series.  Please take a moment to see
       what a :ref:`run series<test-run-series>` is.
    #. Leave the ``start`` date as today.  If you want the run to expire, then
       set the ``end`` date, too.
    #. drag both suites from ``available`` to ``included``
    #. click ``save run``


Isn't this exciting?  You now have a test run series created!
Go tell your boss.


.. _Markdown: http://daringfireball.net/projects/markdown/syntax

