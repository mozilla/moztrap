Product API
===========

Product
-------

.. http:get:: /api/v1/product

Filtering
^^^^^^^^^

    :name: The name of the product to filter on.

    .. sourcecode:: http

        GET /api/v1/product/?format=json&name=Firefox

.. http:get:: /api/v1/product/<id>
.. http:post:: /api/v1/product

Required Fields
^^^^^^^^^^^^^^^

    :name: A string Product name.
    :productversions: A list of at least one Product Version.

Optional Fields
^^^^^^^^^^^^^^^

    :description: A string description.

.. http:delete:: /api/v1/product/<id>

.. note::

    Deleting a Product will delete all of it's child objects.

.. http:put:: /api/v1/product/<id>

.. note::

    ProductVersions are displayed in the GET results. They may be added to
    or changed by a POST request, but a POST to Product will not delete
    any ProductVersion.


Product Version
---------------

.. http:get:: /api/v1/productversion

Filtering
^^^^^^^^^

    :version: The ProductVersion ``name`` to filter
        on.  For example, if the Product and Version are ``Firefox 10`` then
        the ``version`` would be ``10``.
    :product: The Product ``id`` to filter on.
    :product__name: The Product ``name`` to filter on.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/productversion/?format=json&version=10
        GET /api/v1/productversion/?format=json&product__name=Firefox

.. http:get:: /api/v1/productversion/<id>

.. http:post:: /api/v1/productversion

Required Fields
^^^^^^^^^^^^^^^

    :version: A string ProductVersion name.
    :product: A resource uri of the parent Product.

Optional Fields
^^^^^^^^^^^^^^^

    :codename: A string codename.

.. http:delete:: /api/v1/productversion/<id>
.. http:put:: /api/v1/productversion/<id>

.. note::

    The Product of an existing ProductVersion may not be changed.
