Welcome to Case Conductor
=========================

Case Conductor is a test case manager.

Quickstart
----------

Case Conductor requires `Python`_ 2.6 or 2.7 and `MySQL`_ 5+.

(These quickstart instructions assume that you have `virtualenv`_ and
`virtualenvwrapper`_; if you'd rather just install everything globally, skip
step 2.)

1. ``git clone --recursive git://github.com/mozilla/caseconductor``
2. ``mkvirtualenv caseconductor``
3. ``bin/install-reqs``
4. ``echo "CREATE DATABASE caseconductor CHARACTER SET utf8" | mysql``
5. ``./manage.py syncdb --migrate``
6. ``./manage.py create_default_roles``
7. ``./manage.py runserver``
8. Visit http://localhost:8000 in your browser.

Congratulations! If that all worked, you have a functioning instance of Case
Conductor for local testing and experimentation, or :doc:`developing
<development>` Case Conductor.

If this is a production deployment of Case Conductor, please read the
:doc:`deployment` documentation for important security and other
considerations.


Details and trouble-shooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Clone the repository
'''''''''''''''''''''''

First, clone the `Case Conductor repository`_.

.. _Case Conductor repository: https://github.com/mozilla/caseconductor

Dependency source distribution tarballs are stored in a git submodule, so you
either need to clone with the ``--recursive`` option, or after cloning, from
the root of the clone, run::

    git submodule init; git submodule update


2-3. Install the Python dependencies
''''''''''''''''''''''''''''''''''''

If you want to run this project in a `virtualenv`_ to isolate it from other
Python projects on your system, create the virtualenv and activate it. Then run
``bin/install-reqs`` to install the dependencies for this project into your
Python environment.


4. Create a database
''''''''''''''''''''

You'll need a MySQL database. If you have a local MySQL server and your user
has rights to create databases on it, just run this command to create the
database::

    echo "CREATE DATABASE caseconductor CHARACTER SET utf8" | mysql

(If you are sure that UTF-8 is the default character set for your MySQL server,
you can just run ``mysqladmin create caseconductor`` instead).

If you get an error here, your shell user may not have permissions to create a
MySQL database. In that case, you'll need to append ``-u someuser`` to the end
of that command, where ``someuser`` is a MySQL user who does have permission to
create databases. And before going on to step 5, you'll also need to create a
``cc/settings/local.py`` file that specifies the database username to use. See
``cc/settings/local.sample.py`` for a sample that can be copied to
``cc/settings/local.py`` and modified as needed.


5. Create the database tables
'''''''''''''''''''''''''''''

Run ``./manage.py syncdb --migrate`` to install the database tables.


6. Create the default user roles
''''''''''''''''''''''''''''''''

This step is not necessary; you can create your own user roles with whatever
sets of permissions you like. But to create a default set of user roles and
permissions, run ``./manage.py create_default_roles``.


7. Run the development server
'''''''''''''''''''''''''''''

Run ``./manage.py runserver`` to run the local development server. This server
is a development convenience; it's inefficient and probably insecure and should
not be used in production.

8. All done!
''''''''''''

You can access Case Conductor in your browser at http://localhost:8000.

.. _Python: http://www.python.org
.. _MySQL: http://www.mysql.com
.. _virtualenv: http://www.virtualenv.org
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/


Contents
--------

.. toctree::
   :maxdepth: 2

   development
   deployment
   userguide/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
