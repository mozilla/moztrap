Coding Standards
================

Python
------

Testing
~~~~~~~

All tests should pass, and 100% line and branch test coverage should be
maintained, at every commit (on the master branch or a release branch;
temporary failing tests or lack of coverage on a feature branch is acceptable,
but the branch should meet these standards before it is merged.)

To check coverage, run ``bin/test`` and load ``htmlcov/index.html`` in your
browser.

Test methods should set up preconditions for a single action, take that action,
and check the results of that single action (generally, separate these three
blocks in the test method with blank lines). Multiple asserts in a single test
method are acceptable only if they are checking multiple aspects of the result
of a single action (even in that case, multiple test methods may be better
unless the aspects are closely related). Avoid multi-step tests; they should be
broken into separate tests.

Avoid importing the code under test at module level in the test file; instead,
import it in helper methods that are called by the tests that use it. This
ensures that even broken imports cause only the affected tests to fail, rather
than the entire test module.

Prefer helper methods to ``TestCase.setUp`` for anything beyond the most basic
setup (e.g. creating a user for authenticated-view tests); this keeps the setup
more explicit in the test, and avoids doing unnecessary setup if not all test
methods require exactly the same setup.

Never use external data fixtures for test data; use the object factories in
``tests.factories`` (available as ``self.F`` on every
``tests.cases.TestCase``.) If a large amount of interconnected data is needed,
write helper methods. External data fixtures introduce unnecessary dependencies
between tests and are difficult to maintain.


Style
~~~~~

A consistent coding style helps make code easier to read and maintain. Many of
these rules are a matter of preference and an alternative choice would be
equally fine, but follow them anyway for the sake of consistency within this
codebase.

If in doubt, follow :pep:`8`, Python's own style guide.


License blocks
''''''''''''''

Every code module should include the standard license comment header block.


Line length
'''''''''''

Limit all lines to a maximum of 79 characters.


Whitespace
''''''''''

Use four-space indents. No tabs.

Strip all trailing whitespace. Configure your editor to show trailing
whitespace, or automatically strip it on save. ``git diff --check`` will also
warn about trailing whitespace.

Empty lines consisting of only whitespace are also considered "trailing
whitespace". Empty lines should *not* be "indented" with trailing whitespace to
match surrounding code indentation.


Docstrings
''''''''''

Follow :pep:`257`. Every module, class, and method should have a
docstring. Every docstring should begin with a single concise summary line
(that fits within the 79-character limit). If the summary line is the entire
docstring, format it like this::

    def get_lib_dir():
        """Return the lib directory path."""


If there are additional explanatory paragraphs, place both the opening and
closing triple-quotes on their own lines. Separate paragraphs with blank lines,
and add an additional blank line before the closing triple quote::

    def get_lib_dir():
        """
        Return the lib directory path.

        Checks the ``LIB_DIR`` environment variable and the ``lib-dir`` config
        file option before falling back to the default.

        """

Docstrings should be formatted using `reStructuredText`_. This means that
literals should be enclosed in double backticks, and literal blocks indented
and opened with a double colon.

Always use triple double-quotes for enclosing docstrings.

.. _reStructuredText: http://docutils.sourceforge.net/rst.html


Line continuations
''''''''''''''''''

Never use backslash line continuations, use Python's implicit line
continuations within brackets/braces/parentheses. If necessary, prefer
extraneous grouping parentheses to a backslash continuation.

All indents should be exactly four spaces.

The first place to wrap a long line is immediately after the first opening
parenthesis, brace or bracket::

    foo.some_long_method_name(
        arg_one, arg_two, arg_three, keyword="arg")
    
    my_dict = {
        "foo": "bar", "boo": "baz"}
    
    my_list_comprehension = [
        x[0] for x in my_list_of_tuples]

If the second line is still too long, each element/argument should be placed on
its own line. All lines should include a trailing comma, and the closing
brace/paren should go on its own line. (This allows easy rearrangement or
addition/removal of items with full-line cut/paste). For example::

    foo.some_long_method_name(
        foo=foo_arg,
        bar=bar_arg,
        baz=baz_arg,
        something_else="foo",
        )
    
    my_dict = {
        "foo": "bar",
        "boo": "baz",
        "something else": "foo",
        }
    
    my_list_comprehension = [
        x[0] for x in my_list_of_tuples
        if x[1] is not None
        ]


One exception to the four-space indents rule is when a line continuation occurs
in an ``if`` test or another block-opening clause. In this case, indent the
hanging lines eight spaces to avoid visual confusion between the line
continuations and the start of the code block::

    if (something and
            something_else and
            something_else_again):
        do_something()


Comments
''''''''

Code comments should not be used excessively; they require maintenance just as
code (an out-of-date comment is often far worse than no comment at
all). Comments should add information or context or rationale to the code, not
simply restate what the code is doing.

The need for a comment sometimes indicates code that is overly clever or doing
something unexpected. Consider whether the code should be expanded for clarity,
or the API improved so the behavior is less surprising, before adding a
comment.

Use ``@@@`` in a comment to mark code that requires future attention. This
marker should always appear with explanation of why more attention is needed,
or what is missing from the current code.


Quotes
''''''

Always use double-quotes for quoting string literals, unless the quoted string
must contain a double-quote character. Quoting such a string with single quotes
is preferable to using backslash escapes in the string.


Javascript
----------

Javascript code should pass `JSLint`_.

.. _ JSLint: http://www.jslint.com
