.. _tutorial-start-testing:

Moztrap Tutorial, part 4
========================

You have now built all the parts you need to start testing your product.
Allons-y! (Let's go!)

Start Testing
-------------

There are a few ways to get to your test run to execute it.

Run Tests Steps
^^^^^^^^^^^^^^^
    #. Navigate to ``run tests``.
    #. In the finder, click ``SpeckDetector``.
    #. Click ``1.0``.
    #. Click ``feature complete``.
    #. This is a :ref:`run series<test-run-series>` so you will be asked to enter
       a ``build``.  Let's pretend this is your 5th feature complete build.
       Here type: ``FC-5``
    #. Set ``location`` to ``field``.
    #. Click ``run tests in feature complete``.


Manage Runs Steps
^^^^^^^^^^^^^^^^^
    #. Navigate to ``manage | runs``.
    #. Find the ``feature complete`` run.
    #. Expand the arrow on the left to display the details of that run.
    #. Click the green button that says ``run tests in feature complete``.
    #. .. note::
            if you want to send this URL to your testers in an email, then just
            right-click that same button and select ``copy link location``.
    #. Specify your environment, as above.

"I got a URL!" Steps
^^^^^^^^^^^^^^^^^^^^
    #. If somebody gave you a URL to their run or run series, then click on it.
    #. Specify your environment, as above.

Pass a Test
-----------
Some tests pass, some fail.  This is the way of the world.  Let's pass this
one.

    #. Click the title or expansion arrow of ``update firmware``.
    #. Click ``pass test``.
    #. That was easy.

Fail a Test
-----------

    #. Click the title or expansion arrow of ``Detect a pollen speck``.
    #. Click ``fail test`` next to the first step.
    #. You must provide some explanation for the failure::

        We applied the cortical electrodes but were
        unable to get a neural reaction from the
        pollen speck.

    #. Specifying a bug URL is optional, but it's a good idea.  I'll leave
       that up to you.


You're done with the run!  This is fantastic!  If only those kids from High
School could see you *now!*