Tags API
========

Tag
---

.. http:get:: /api/v1/tag

Filtering
^^^^^^^^^

    :name: The Tag ``name`` to filter on.
    :product: The Product ``id`` to filter on.
    :product__name: The Product ``name`` to filter on.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/tag/?format=json

.. http:get:: /api/v1/tag/<id>
.. http:post:: /api/v1/suite

Required Fields
^^^^^^^^^^^^^^^

    :name: A string name for the Tag.
    :product: A resource uri to a Product.

Optional Fields
^^^^^^^^^^^^^^^

    :description: A string description for the Tag.

.. http:delete:: /api/v1/suite/<id>
.. http:put:: /api/v1/suite/<id>

.. note::

    The Tag's Product may not be changed unless the tag is not in use, the
    product is being set to None, or the product matches the existing cases."
