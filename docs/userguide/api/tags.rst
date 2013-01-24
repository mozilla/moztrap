Tags API
=============

Tag
--------

.. http:get:: /api/v1/tag
.. http:post:: /api/v1/suite
.. http:delete:: /api/v1/suite/<id>
.. http:put:: /api/v1/suite/<id>

Filtering
^^^^^^^^^

    :name: The name of the tag.
    :product: The id of the product.
    :product__name: The name of the product

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/tag/?format=json
