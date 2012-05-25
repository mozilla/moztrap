.. _faq:

Frequently Asked Questions
==========================

1. **Why don't all of my test cases don't show up when I execute my test run?**

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

2. **Why don't I see the results I expect when I type in a filter?**

  - When you type text into the simple search field, you'll see a drop-down
    list showing some possible choices.  On the right of that list is the field
    to which that filter will be applied.  If you filter for the word "Red" in
    the :ref:`product <products>` field, but there is no product with the word
    "Red" in it, then you may see a list with no results.  When you type your
    filter word, use the arrow keys to select the field to filter on.

3. **How can I create a test case with no steps?**

  - By default, all test cases have steps, and a step has a required field of
    `instruction`.  If you try to save the case when there is an empty
    instruction, it will say that you must fill out that field.  To avoid this,
    simply click the "X" next to that step, it will be deleted, and you can
    save your case without steps.

4. **Please help us add more to the FAQ!**

  - New FAQ items help everyone.  Your contributions help!