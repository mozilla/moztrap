Product API
===========

Product
-------

.. http:get:: /api/v1/product
.. http:post:: /api/v1/product
.. http:delete:: /api/v1/product/<id>
.. http:put:: /api/v1/product/<id>

Filtering
^^^^^^^^^

    :name: The name of the product to filter on.

    .. sourcecode:: http

        GET /api/v1/product/?format=json&name=Firefox


Product Version
---------------

.. http:get:: /api/v1/productversion
.. http:post:: /api/v1/productversion
.. http:delete:: /api/v1/productversion/<id>
.. http:put:: /api/v1/productversion/<id>

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
