Data Import Formats
===================

.. _data-import:

JSON 
----

JSON is a great way to import more complex sets of :ref:`cases <test-cases>`, :ref:`suites
<test-suites>` and :ref:`product <products>` definitions.  

**Note:** The JSON you choose to import must be encoded in UTF8.

Example::

    {
        "Products": [
            {
                "name": "product name",
                "description": "product description"
            },
            {
                "name": "product name",
                "description": "product description"
            }
        ],
        "Suites": [
            {
                "name": "suite name",
                "description": "suite description",
                "product": "product name"
            }
        ],
        "Cases": [
            {
                "title": "case title",
                "description": "case description",
                "product": "product name",
                "tags": ["tag1", "tag2", "tag3"],
                "suites": ["suite1", "suite2", "suite3"],
                "steps": [
                    {
                        "action": "action text",
                        "expected": "expected text"
                    },
                    {
                        "action": "action text",
                        "expected": "expected text"
                    }
                ]
            }
        ]
    }

CSV (future)
------------

When importing from a spreadsheet or wiki set of test cases, this may prove a very useful
format.  This doesn't handle multiple separate steps in test cases.  Rather, it presumes
all steps are in a single step when imported to Case Conductor.

Bulk Test Case Entry Formats
============================

Gherkin-esque
-------------

This is one of the test case formats supported in the bulk test case creator.

Format::

    Test that <test title>
    When <instruction>
    Then <expected result>

Example::

    Test that I can write a test
    When I execute my first step instruction
    then the expected result is observed
    And when I execute mysecond step instruction
    Then the second step expected result is observed
    
Markdown (future)
-----------------

Description:
This will be another format for the bulk test case creator.

Details TBD.