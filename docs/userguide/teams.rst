.. _teams:

Teams
=====

Any :ref:`product<products>`, :ref:`product version<product-versions>`, or
:ref:`test run<test-runs>` can optionally have a **Team**, which is just a set
of users. Teams are not named or managed as an independent entity; they are
simply a set of users associated with a given product, version, or run.

Teams are inherited by default; any product version without its own team
explicitly set will inherit its product's team, and any test run without a team
set will inherit its product version's team. Unlike :ref:`environment
inheritance<environment-inheritance>`, there is no subset requirement - a test
run can be explicitly assigned any team, even if some members of that team are
not part of the product version or product's team.

When a test run is activated, all team members for that test run will
automatically be assigned all test cases in that run.
