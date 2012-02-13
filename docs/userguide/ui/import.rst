Data Import Formats
===================

.. _data-import:

.. note::

   Imported data should always be UTF-8 encoded.


JSON
----

JSON is a great way to import more complex sets of :ref:`cases <test-cases>`
and :ref:`suites <test-suites>` for your product. One JSON file will be used
per :ref:`product <products>` :ref:`version <product-versions>`. Simply use the
user interface to create the :ref:`Product <products>` and :ref:`Version
<product-versions>` that applies to the :ref:`cases <test-cases>` and
:ref:`suites <test-suites>` to be imported. Then just import your JSON file to
that :ref:`product version <product-versions>`.

The "suites" section is optional.  It's only needed if you want to apply a
description to your suites.  All suites specified in cases will be created
on the fly if they're not found.

Example::

    {
        "suites": [
            {
                "name": "suite name",
                "description": "suite description"
            }
        ],
        "cases": [
            {
                "title": "case title",
                "description": "case description",
                "tags": ["tag1", "tag2", "tag3"],
                "suites": ["suite1 name", "suite2 name", "suite3 name"],
                "steps": [
                    {
                        "instruction": "instruction text",
                        "expected": "expected text"
                    },
                    {
                        "instruction": "instruction text",
                        "expected": "expected text"
                    }
                ]
            }
        ]
    }


CSV (future)
------------

When importing from a spreadsheet or wiki set of test cases, this may prove a
very useful format.  This doesn't handle multiple separate steps in test cases.
Rather, it presumes all steps are in a single step when imported to Case
Conductor.


Bulk Test Case Entry Formats
============================

Gherkin-esque
-------------

This is one of the test case formats supported in the bulk test case creator.

Format::

    Test that <test title>
    <description text>
    When <instruction>
    Then <expected result>

Example::

    Test that I can write a test
    This test tests that a user can write a test
    When I execute my first step instruction
    then the expected result is observed
    And when I execute mysecond step instruction
    Then the second step expected result is observed


Markdown (future)
-----------------

This will be another format for the bulk test case creator.

Example::

    Test case 1 title here
    ======================
    Description text here

    * which can contain bullets
    * **with formatting**
       * indentation
       * [and links](www.example.com)

    Steps
    -----
    1. Step 1 action
        * Step 1 Expected Result
    2. Step 2 action
        * Step 2 Expected Result

    Test case 2 title here
    ======================
    ...
