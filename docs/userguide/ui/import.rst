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

Simple Example::

    {
        "suites": [
            {
                "name": "suite name",
                "description": "suite description"
            }
        ],
        "cases": [
            {
                "name": "case title",
                "description": "case description",
                "tags": ["tag1", "tag2", "tag3"],
                "suites": ["suite1 name", "suite2 name", "suite3 name"],
                "created_by": "cdawson@mozilla.com",
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

Both top-level sections ("suites" and "cases") are optional.  However, if either
section is included, each item requires a "name" field value.  Other than that,
all fields are optional.

Importing
---------
Importing test cases with this method involves the use of a ``management
command``.  Before you import the cases, you must create your Product and
:ref:`product version <product-versions>` in the user interface as mentioned
above.  If the :ref:`suites <test-suites>` in your JSON file do not already
exist, they will be created for you.

Import command
--------------
Importing involves a ``management command`` on the command line.  For this
example, we are importing test cases from a file called ``MyCases.json`` to 
version ``1.0`` of product ``Foo``.  .

1. cd into your MozTrap directory
2. ``./manage.py import Foo 1.0 MyCases.json``

That should be it.  Now go back to the web interface and your cases will be
imported.


CSV (future)
------------

When importing from a spreadsheet or wiki set of test cases, this may prove a
very useful format.  This doesn't handle multiple separate steps in test cases.
Rather, it presumes all steps are in a single step when imported to MozTrap.


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
