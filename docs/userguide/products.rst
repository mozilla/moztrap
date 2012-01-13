.. _products:

Products
========

The core object in Case Conductor is the **Product**. A Product itself is
little more than a name and optional description, but almost every other object
in the Case Conductor data model relates to a Product either directly or
indirectly.

.. _product-versions:

Products have a list of *versions*; every :ref:`test run <test-runs>` and
:ref:`test case <test-cases>` applies to a particular version of the product.

Product versions are automatically ordered according to their *version*
number/name. The version is split into dotted segments, and the segments are
ordered lexicographically (with implicit left-side zero-padding of numerals to
avoid e.g. "2" ordering after "11"). So, for instance, version *1.1* is greater
than version *1.0.3*, version *2.0b1* is greater than *2.0a3*, and *3.11.1* is
greater than *3.2.0*.

There are some special cases to better support common version-numbering
schemes. Strings alphabetically prior to "final" are considered pre-release
versions (thus *2.1a*, *2.1alpha*, and *2.1b* are all prior to *2.1*, whereas
*2.1g* is considered a post-release patchlevel). The strings "rc", "pre", and
"preview" are considered equivalent to "c" (thus also pre-release), and the
string "dev" orders before "alpha" and "beta" (so *2.1dev* is prior to *2.1a*).

Product versions can also optionally have a *code name* that does not impact
their ordering.
