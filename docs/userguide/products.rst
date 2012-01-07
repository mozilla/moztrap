.. _products:

Products
========

The core object in Case Conductor is the Product. A Product itself is little
more than a name and optional description, but almost every other object in the
Case Conductor data model relates to a Product either directly or indirectly.

Products have a list of *versions*; each :ref:`test run <test-runs>` applies to
a particular version of the product.
