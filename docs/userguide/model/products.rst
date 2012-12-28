.. _products:

Products
========

The core object in MozTrap is the **Product**. A Product itself is little
more than a name and optional description, but almost every other object in the
MozTrap data model relates to a Product either directly or indirectly.

Products have a list of :ref:`versions <product-versions>`; every
:ref:`test run <test-runs>` and :ref:`test case version<test-cases>` applies
to a particular version of the product.

.. _product-edit-fields:

Product Edit Fields
^^^^^^^^^^^^^^^^^^^

* **Name** - The name of the Product. (Firefox, Thunderbird, etc)
* **Description** - (optional) A brief description of the product.
* **Version** - Every Product must have at least one Product Version.  Many
  Products will end up with several Product Versions. (1.0, 2.0, 2.5,
  etc).  If this is a web project and you don't want several versions, feel
  free to call this whatever you like (Production, Current, etc.).
* **Environments** - This is a pre-existing collection of environments called
  an :ref:`Environment Profile <environment-profiles>`.  You can specify this
  at creation time, or later.  Note that the set of environments can be
  different for different Product Versions because the needs of your product
  may change over time.  When you want to update the list of supported
  environments, you do this on the Product Version rather than the Product
  itself.

.. _product-versions:

Product Versions
================

When a new **Product Version** is created, all test cases for that Product will
get a new version to match the new **Product Version**.

For more information on how Test Cases and Product Versions relate while
running tests against different builds of a Product, see the :ref:`Test Runs
<test-runs>` section.

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


Fill Case Versions
^^^^^^^^^^^^^^^^^^

.. _product-version-fill-cases:

Test cases have a version for each Product Version.
If you have multiple product versions, it is possible to have a version of a
case for one product version and not for another.  For example, given:

* Product Foo

  * Version 1.0
  * Version 2.0

* Case A

  * Case A, Version 1.0

You can see here that you have a version of the *Case A* for
*Product Foo Version 1.0*, but not for *Version 2.0*.  With a large
project, you may find yourself with hundreds of cases where you created them
for Version 1.0 and not for 2.0.

If you want to create those versions, you have 2 options:

1. If you only have a few, you can edit the case in question, and in the upper
   right of the dialog, click the version field and select
   *+2.0 (add this version)*
2. Edit the product version and specify the other version in the
   ``Fill Cases From`` field.



.. _product-version-edit-fields:

Product Version Create Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Product** - The Product that this is a version of.
* **Copy Environments and Cases From** - (optional) Environments
  apply to each product version.  Each version can have a unique set of
  environments.  But commonly, they are very close, and the set of environments
  evolves over time.  This field allows you to choose which existing product
  version to copy the environments from.  You can then add or remove from the
  list of environments for this version.

Fields in both Create and Edit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Version** - The name of the new version.  See
  :ref:`product versions <product-versions>` for more info on how order of
  versions works.
* **Codename** - (optional) This can be any text and is only used as a
  reference in the summary list of versions when there is another name for a
  version.  For instance, for Mac OS 10.7, the Codename is *Lion*.


Product Version Edit Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Fill Cases From** - (optional) The product version to copy cases
  from if they don't exist for this product version yet.  See
  :ref:`Fill Case Versions<product-version-fill-cases>`.
