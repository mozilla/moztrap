Installation
============

Clone the repository
--------------------

First, clone the `Case Conductor repository`_.

.. _Case Conductor repository: https://github.com/mozilla/caseconductor

Dependency source distribution tarballs are stored in a git submodule, so you
either need to clone with the ``--recursive`` option, or after cloning, from
the root of the clone, run::

    git submodule init; git submodule update


Install the Python dependencies
-------------------------------

If you want to run this project in a `virtualenv`_ to isolate it from other
Python projects on your system, create the virtualenv and activate it. Then run
``bin/install-reqs`` to install the dependencies for this project into your
Python environment.

.. _virtualenv: http://www.virtualenv.org


Create a database
-----------------

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


Create the database tables
--------------------------

Run ``./manage.py syncdb --migrate`` to install the database tables.


Create the default user roles
-----------------------------

This step is not necessary; you can create your own user roles with whatever
sets of permissions you like. But to create a default set of user roles and
permissions, run ``./manage.py create_default_roles``.


Run the development server
--------------------------

Run ``./manage.py runserver`` to run the local development server. This server
is a development convenience; it's inefficient and probably insecure and should
not be used in production.

All done!
---------

You can access Case Conductor in your browser at http://localhost:8000.
