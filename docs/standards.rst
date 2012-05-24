Coding Standards
================

.. contents:: :local:

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
``tests.cases.DBTestCase``.) If a large amount of interconnected data is
needed, write helper methods. External data fixtures introduce unnecessary
dependencies between tests and are difficult to maintain.


Style
~~~~~

A consistent coding style helps make code easier to read and maintain. Many of
these rules are a matter of preference and an alternate choice would serve
equally well, but follow them anyway for the sake of consistency within this
codebase.

If in doubt, follow :pep:`8`, Python's own style guide.


Line length
'''''''''''

Limit all lines to a maximum of 79 characters.


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


Imports
'''''''

Outside of test code, prefer module-level imports to imports within a function
or method. If the latter are necessary to avoid circular imports, consider
reorganizing the dependency hierarchy of the modules involved to avoid the
circular dependency.

Module-level imports should all occur at the top of the module, prior to any
other code in the module. The following types of imports should appear in the
following order (omitted if not present), each group of imports separated from
the next by a single blank line:

1. Python standard library imports.

2. Django core imports.

3. Django contrib imports.

4. Other third-party module imports.

5. Imports from other modules in MozTrap.

Within each group, order imports alphabetically.

For imports from within MozTrap, use explicit relative imports for imports
from the same package or the parent package (i.e.  where the explicit
relative import path begins with one or two dots).  For more distant
imports, it's usually more readable to give the full absolute path.  Thus,
for code in ``moztrap.view.manage.runs.views``, you could do ``from .forms
import AddRunForm`` and ``from ..cases.forms import AddCaseForm``, but it's
probably better to do ``from moztrap.view.lists import decorators`` rather
than ``from ....lists import decorators``; more than two dots become
difficult to distinguish visually.

Never use implicit relative imports; if an import does not begin with a dot, it
should be a top-level module. In other words, if ``models.py`` is a sibling
module, always ``from . import models``, never just ``import models``.


Whitespace
''''''''''

Use four-space indents. No tabs.

Strip all trailing whitespace. Configure your editor to show trailing
whitespace, or automatically strip it on save. ``git diff --check`` will also
warn about trailing whitespace.

Empty lines consisting of only whitespace are also considered "trailing
whitespace". Empty lines should *not* be "indented" with trailing whitespace to
match surrounding code indentation.

Separate classes and module-level functions with three blank lines. Separate
class methods with two blank lines. Single blank lines may be used within
functions and methods to logically group lines of code.


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

.. _JSLint: http://www.jslint.com
