.. _roles:

Roles and Permissions
=====================

.. _default-roles:

Default roles
-------------

Four default roles are created when you run ``python manage.py
create_default_roles``: :ref:`Tester<tester-role>`, :ref:`Test
Creator<test-creator-role>`, :ref:`Test Manager<test-manager-role>`, and
:ref:`Admin<admin-role>`. These roles can be fully customized, and new ones can
be created (currently only via the Django admin at ``/admin/``).

The default roles have the following permissions:


.. _tester-role:

Tester
~~~~~~

* :ref:`execute`


.. _test-creator-role:

Test Creator
~~~~~~~~~~~~

All :ref:`Tester<tester-role>` permissions, plus:

* :ref:`create_cases`
* :ref:`manage_suite_cases`


.. _test-manager-role:

Test Manager
~~~~~~~~~~~~

All :ref:`Tester<tester-role>` and :ref:`Test Creator<test-creator-role>`
permissions, plus:

* :ref:`manage_cases`
* :ref:`manage_suites`
* :ref:`manage_tags`
* :ref:`manage_runs`
* :ref:`review_results`
* :ref:`manage_environments`


.. _admin-role:

Admin
~~~~~

All :ref:`Tester<tester-role>`, :ref:`Test Creator<test-creator-role>` and
:ref:`Test Manager<test-manager-role>` permissions, plus:

* :ref:`manage_products`
* :ref:`manage_users`

When setting up MozTrap, running the command ``python manage.py
create_default_roles`` will ask to create an admin user.  This special first
admin has all these privileges:

* **Admin role in the MozTrap UI**:  This gives the user the ability to visit
  the ``Manage | Users`` area of the product.  This user can edit other users
  to:

  * assign roles
  * create api keys
  * delete or deactivate
* **Staff Status**:  This gives the user access to the ``/admin/`` url.  This
  is a special *behind the scenes* access to the data in MozTrap.  It is also
  where items that were deleted can be *undeleted*.
* **Superuser Status**:  A user that has this status will always have
  admin privileges in the MozTrap UI, even if their role is changed to
  something other than ``Admin``.

So you can see that this first admin user is special, and also the gateway to
providing access for all other users to be admins.


Permissions
-----------

.. _execute:

execute
~~~~~~~

Can run tests and report the results.


.. _create_cases:

create_cases
~~~~~~~~~~~~

Can create new test cases and edit them (but not edit test cases created by
others). Allows tagging of these test cases with existing tags, but not
creation of new tags.


.. _manage_suite_cases:

manage_suite_cases
~~~~~~~~~~~~~~~~~~

Can add and remove test cases from suites.


.. _manage_cases:

manage_cases
~~~~~~~~~~~~

Can add, edit, and delete test cases and test case versions.


.. _manage_suites:

manage_suites
~~~~~~~~~~~~~

Can add, edit, and delete test suites.


.. _manage_tags:

manage_tags
~~~~~~~~~~~

Can add, edit, and delete tags.


.. _manage_runs:

manage_runs
~~~~~~~~~~~

Can add, edit, and delete test runs.


.. _review_results:

review_results
~~~~~~~~~~~~~~

Can review submitted test results and mark them reviewed.


.. _manage_environments:

manage_environments
~~~~~~~~~~~~~~~~~~~

Can create, edit, and delete environment profiles, categories, elements, and
environments.


.. _manage_products:

manage_products
~~~~~~~~~~~~~~~

Can create, edit, and delete products and product versions.


.. _manage_users:

manage_user
~~~~~~~~~~~

Can create, edit, and delete users.
