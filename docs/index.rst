.. Case Conductor documentation master file, created by
   sphinx-quickstart on Thu Jan  5 18:58:30 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Case Conductor's documentation!
==========================================

Quickstart
----------

Case Conductor requires Python 2.6 or 2.7.

First, update git submodules (dependency source distribution tarballs are
stored in a git submodule). From the root of this repo, run::

    git submodule init; git submodule update

If you want to run this project in a `virtualenv`_ to isolate it from other
Python projects on your system, create the virtualenv and activate it. Then run
``bin/install-reqs`` to install the dependencies for this project into your
Python environment.

You may need to create a ``cc/settings/local.py`` file with some details of
your local database and other configuration. See
``cc/settings/local.sample.py`` for a sample that can be copied to
``cc/settings/local.py`` and modified as needed.

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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
