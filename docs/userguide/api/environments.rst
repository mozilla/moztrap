Environment API
===============

Profile
-------

.. http:get:: /api/v1/profile

Filtering
^^^^^^^^^

    :name: The ``name`` of the Profile to filter on.

.. http:get:: /api/v1/profile/<id>
.. http:post:: /api/v1/profile

Required Fields
^^^^^^^^^^^^^^^

    :name: A string Profile name.

.. http:delete:: /api/v1/profile/<id>
.. http:put:: /api/v1/profile/<id>

Category
--------

.. http:get:: /api/v1/category

Filtering
^^^^^^^^^

    :name: The ``name`` of the Category to filter on.

.. http:get:: /api/v1/category/<id>
.. http:post:: /api/v1/category

Required Fields
^^^^^^^^^^^^^^^

    :name: A string Category name.

.. http:delete:: /api/v1/category/<id>
.. http:put:: /api/v1/category/<id>

Element
-------

.. http:get:: /api/v1/element/

Filtering
^^^^^^^^^

    :name: The ``name`` of the Element to filter on.
    :category: The ``id`` of the Category to filter on.
    :category__name: The ``name`` of the Category to filter on.

.. http:get:: /api/v1/element/<id>
.. http:post:: /api/v1/element

Required Fields
^^^^^^^^^^^^^^^

    :name: A string Element name.
    :category: A resource uri to the parent Category.

.. http:delete:: /api/v1/element/<id>
.. http:put:: /api/v1/element/<id>


.. note::

    The Category of an existing Element may not be changed.

Environment
-----------

.. http:get:: /api/v1/environment

Filtering
^^^^^^^^^

    :elements: (optional) The Element ID to filter on.

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/environment/?format=json&elements=5

.. http:get:: /api/v1/environment/<id>
.. http:post:: /api/v1/environment

Required Fields
^^^^^^^^^^^^^^^

    :profile: A resource uri to the parent Profile.
    :elements: A list of element resource uri's.

.. note:: Each element must be from a separate category.

.. http:delete:: /api/v1/environment/<id>
