.. _faq:

Frequently Asked Questions
==========================

1. **Some or all of my test cases don't show up when I execute my test run**

  - Your :ref:`test cases <test-cases>` or :ref:`test suites <test-suites>` may
    not have been active at the time the :ref:`test run <test-runs>` was made
    active. When a test run is made active, it will take a snapshot of active
    suites and cases at that time. If cases and suites are made active after
    that time, they will not show in that test run: only in newly activated
    test runs. This is because once a test run is activated, it is considered a
    "unit of work" that won't be altered.

  - When you have activated new test cases and/or suites and want a test run to
    reflect that, simply clone the existing test run, and activate it. Your
    newly active cases and suites will be reflected.

2. **When I type in a filter, I don't see the results I expected**

  - When you type text into the simple search field, you'll see a drop-down
    list showing some possible choices.  On the right of that list is the field
    to which that filter will be applied.  If you filter for the word "Red" in
    the :ref:`product <products>` field, but there is no product with the word
    "Red" in it, then you may see a list with no results.  When you type your
    filter word, use the arrow keys to select the field to filter on.