Product API
===========

Product
-------

.. http:get:: /api/v1/product

    Return a list of products and the product versions it owns.


    :format: (required) The API **always** requires a value of ``json`` for this
        field.
    :name: (optional) The name of the product to filter on.
    :limit: (optional) Defaults to 20 items, but can be set higher or lower.  0
        will return all records.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/product/?format=json


Product Version
---------------

.. http:get:: /api/v1/productversion

    Return a list of product versions.

    .. note::

        The underscores in query params (like ``case__suites``) are **DOUBLE**
        underscores.

    :format: (required) The API **always** requires a value of ``json`` for this
        field.
    :version: (optional) The ProductVersion ``name`` to filter
        on.  For example, if the Product and Version are ``Firefox 10`` then
        the ``version`` would be ``10``.
    :product__name: (optional) The Product ``name`` to filter on.
    :limit: (optional) Defaults to 20 items, but can be set higher or lower.  0
        will return all records.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/productversion/?format=json&version=10
        GET /api/v1/productversion/?format=json&product__name=Firefox
