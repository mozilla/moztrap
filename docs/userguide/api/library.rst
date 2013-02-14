Test Cases and Suites API
=========================

For additional information, please consult
https://moztrap.readthedocs.org/en/latest/userguide/model/library.html

Case
____

.. http:get:: /api/v1/case

Filtering
^^^^^^^^^

    :product: The Product ``id`` to filter on.
    :product__name: The Product ``name`` to filter on.
    :suite: The Suite ``id`` to filter on.
    :suite__name: The Suite ``name`` to filter on.

.. http:get:: /api/v1/case/<id>

.. note::

    Suites are displayed in the GET results, for
    informational purposes, but may not be changed.

.. http:post:: /api/v1/case

Required Fields
^^^^^^^^^^^^^^^

    :product: A resource uri to a Product.

Optional Fields
^^^^^^^^^^^^^^^

    :idprefix: A string that will be displayed as part of the case ID.

.. http:delete:: /api/v1/case/<id>
.. http:put:: /api/v1/case/<id>

.. note::

    The product of an existing case may not be changed.

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

.. http:get:: /api/v1/caseversion/<id>

.. note::

    Environments, Tags, Suites and CaseSteps are displayed in the GET results for
    informational purposes, but may not be changed.

.. http:post:: /api/v1/caseversion

Required Fields
^^^^^^^^^^^^^^^

    :case: A resource uri to the parent Case
    :productversion: A resource uri to a ProductVersion

Optional Fields
^^^^^^^^^^^^^^^

    :name: A string name
    :description: A string description
    :status: ``active``, ``draft``, or ``disabled``

.. note::

    The parent Case's Product must match the ProductVersion's Product.

.. http:delete:: /api/v1/caseversion/<id>
.. http:put:: /api/v1/caseversion/<id>

.. note::

    The ``productversion`` and ``case`` fields are not required, and may not be changed.

CaseSteps
---------

.. http:get:: /api/v1/casestep

Filtering
^^^^^^^^^

    :caseversion: The ``id`` of the parent caseversion
    :caseversion__name: The ``name`` of the parent caseversion

.. http:post:: /api/v1/casestep

Required Fields
^^^^^^^^^^^^^^^

    :caseversion: A resource uri to a CaseVersion
    :instruction: A string describing what actions to take
    :number: An integer used to order steps

Optional Fields
^^^^^^^^^^^^^^^

    :expected: The expected result following the instruction

.. http:delete:: /api/v1/casestep/<id>
.. http:put:: /api/v1/casestep/<id>

.. note::

    The CaseVersion of an existing CaseStep may not be changed.

Suites
------

.. http:get:: /api/v1/suite

Filtering
^^^^^^^^^

    :name: The ``name`` of the suite
    :product: The ``id`` of the product for this suite
    :product__name: The ``name`` of the product

    **Example request**:

    .. sourcecode:: http

        GET /api/v1/suite/?format=json

.. http:post:: /api/v1/suite

Required Fields
^^^^^^^^^^^^^^^

    :product: A resource uri to a Product

Optional Fields
^^^^^^^^^^^^^^^

    :name: A string name
    :description: A string description
    :status: ``active``, ``draft``, or ``disabled``


.. http:delete:: /api/v1/suite/<id>
.. http:put:: /api/v1/suite/<id>

.. note::

    The Product of an existing Suite may not be changed.

SuiteCase
----------

.. http:get:: /api/v1/suitecase
.. http:get:: /api/v1/suitecase/<id>
.. http:post:: /api/v1/suitecase

Required Fields
^^^^^^^^^^^^^^^

    :case: A resource uri to a case
    :suite: A resource uri to a suite
    :order: An integer used to sort the cases within the suite.

.. note::

    The Case's Product must match the Suite's Product.

.. http:delete:: /api/v1/suitecase/<id>
.. http:put:: /api/v1/suitecase/<id>

.. note::

    Only the order may be changed for an existing SuiteCase.

