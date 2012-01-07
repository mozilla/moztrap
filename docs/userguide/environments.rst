.. _environments:

Environments
============

Case Conductor allows fine-grained and flexible specification of the
environment(s) in which each test should be run.

An **Environment** is a collection of :ref:`environment
elements<environment-elements>` that together define the conditions for a
single run of a test. For instance, an environment for testing a web
application might consist of a browser, an operating system, and a language; so
one environment might be **Firefox 10, OS X, English**, and another **Internet
Explorer 9, Windows 7, Spanish**.

.. _environment-elements:

An **Environment Element** is a single element of a test environment,
e.g. **Windows 7** or **Firefox 10**.

.. _environment-categories:

A **Environment Category** is a category containing several (generally mutually
exclusive) elements. For instance, the **Operating System** category might
contain the elements **OS X 10.5**, **OS X 10.6**, **Windows Vista**, and
**Windows 7**.

.. _environment-profiles:

An **Environment Profile** is a collection of :ref:`environments` that
specifies the supported environments for testing a product or type of
product. For instance, a **Web Applications** environment profile might contain
a set of environments where each one specifies a particular combination of web
browser, operating system, and language.

Environment profiles can be named and maintained independently of any specific
product; these generic profiles can then be used as the initial profile for a
new product. For instance, the generic **Web Applications** profile described
above could be used as the initial profile for a new web application
product.

:ref:`Products`, :ref:`cycles<test-cycles>`, :ref:`runs<test-runs>`, and
:ref:`test cases<test-cases>` all have their own environment profile; that is,
the set of environments relevant for testing that particular product, test
cycle, test run, or test case. These profiles are
:ref:`inherited<environment-inheritance>`.


Auto-generation
---------------

Given a set of :ref:`environment categories<environment-categories>` (or
subsets of the :ref:`elements<environment-elements>` from each
:ref:`category<environment-categories>`) Case Conductor can auto-generate an
environment profile containing every possible combination of one element from
each category.

For instance, given the :ref:`elements<environment-elements>` **Firefox** and
**Opera** in the :ref:`category<environment-categories>` **Browser** and the
elements **Windows** and **OS X** in the category **Operating System**, the
auto-generated profile would contain the :ref:`environments` **Firefox,
Windows**; **Firefox, OS X**; **Opera**, **Windows**; and **Opera, OS X**.


.. _environment-inheritance:

Inheritance
-----------

At the highest level, a product's environment profile describes the full set of
environments that the product supports and should be tested in.

A test cycle or test case by default inherits the full environment profile of
its product. This profile can be narrowed from the product's profile: for
instance, if a particular test case only applies to the Windows version of the
product, all non-Windows environments could be eliminated from that test case's
environment profile. Similarly, a test cycle could be designated as
Esperanto-only, and all non-Esperanto environments would be removed from its
profile (ok, that's not very likely).

The environment profile of a test case or test cycle is limited to a subset of
the parent product's profile - it doesn't make sense to write a test case or
run a test cycle for a product on environments the product itself does not
support.

Similarly, a test run inherits its initial environment profile from its parent
test cycle; its profile can be narrowed but not expanded beyond the profile of
its cycle.

When a test case is included in a test run, the resulting "executable case"
gets its own environment profile: the intersection of the environment profiles
of the test run and the test case. So, for example, if the above Windows-only
test case were included in an Esperanto-only test run, that case, as executed
in that run, would get an even smaller environment profile containing only
Windows Esperanto environments.

Thus, the inheritance tree for environment profiles looks something like this::

    Product
     /     \
    Cycle  Case
     |      |
    Run     |
      \     |
      executable Case


Cascades
~~~~~~~~

Whenever an environment is removed from an object's profile, that removal
cascades down to all children of that object. So removing an environment from a
product's profile cascades to all that product's cycles and cases, and removing
an environment from a cycle's profile cascades to its runs.

Adding an environment only cascades in certain situations. Adding an
environment to a product's profile cascades to cycles and runs only if they are
still in Draft state; once they are activated, their environment profile can
only be added to manually.

Additions to a product's environment profile cascade only to those test cases
whose environment profile is still identical to the product's environment
profile (i.e. test cases that apply to all environments the product
supports). Once a test case has been narrowed to a subset of the product's full
environment profile, additions to the product's profile will have to be
manually added to the case's profile if the new environment applies to that
case.

:ref:`Test results<test-results>`, once recorded, are never deleted, even if
their corresponding environment is removed from their product, cycle, or run's
environment profile.
