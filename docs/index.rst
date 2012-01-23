Welcome to Case Conductor
=========================

Quickstart
----------

Case Conductor requires Python 2.6 or 2.7.

First, clone the `Case Conductor repository`_.

.. _Case Conductor repository: https://github.com/mozilla/caseconductor

Then update git submodules (dependency source distribution tarballs are stored
in a git submodule). From the root of this repo, run::

    git submodule init; git submodule update

If you want to run this project in a `virtualenv`_ to isolate it from other
Python projects on your system, create the virtualenv and activate it. Then run
``bin/install-reqs`` to install the dependencies for this project into your
Python environment.

You'll need a MySQL database. If you have a local MySQL server and your user
has rights to create databases on it, ``mysqladmin create caseconductor``
should be all that's needed.

If your database is named ``caseconductor`` and is accessible at localhost
under your shell username, the default settings should be fine for
:doc:`development` and experimentation with Case Conductor. If your setup is
different, you'll need to create a ``cc/settings/local.py`` file with some
details of your configuration. See ``cc/settings/local.sample.py`` for a sample
that can be copied to ``cc/settings/local.py`` and modified as needed. (If this
is a production deployment, please read the :doc:`deployment` documentation for
important security and other considerations.)

Once this configuration is done, you should be able to run ``./manage.py syncdb
--migrate`` to install the database tables, ``./manage.py runserver`` to run
the local development server, and then access the test case manager in your
browser at ``http://localhost:8000``.

To create the default set of user roles with the default permissions, run
``./manage.py create_default_roles``.

.. _virtualenv: http://www.virtualenv.org


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
