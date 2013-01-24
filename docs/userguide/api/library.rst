Test Cases and Suites API
=========================

Case Version
------------

.. http:get:: /api/v1/caseversion

Filtering
^^^^^^^^^

    :productversion: The ProductVersion ``id`` to filter on.
    :productversion__version: The ProductVersion ``name`` to filter
        on.  For example, if the Product and Version are ``Firefox 10`` then
        the ``productversion__version`` would be ``10``.
    :productversion__product__name: The Product ``name`` to filter on.
    :case__suites: The Suite ``id`` to filter on.
    :case__suites__name: The Suite ``name`` to filter on.
    :tags__name: The tag ``name`` to filter on.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/caseversion/?format=json&productversion__version=10&case__suites__name=Sweet%20Suite
        GET /api/v1/caseversion/?format=json&productversion__product__name=Firefox

Suites
------

.. http:get:: /api/v1/suite
.. http:post:: /api/v1/suite
.. http:delete:: /api/v1/suite/<id>
.. http:put:: /api/v1/suite/<id>

Filtering
^^^^^^^^^

    :name: The ``name`` of the suite
    :product: The ``id`` of the product for this suite
    :product__name: The ``name`` of the product

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/suite/?format=json

