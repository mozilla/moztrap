Installation
============

.. _quickstart:

Quickstart
----------

MozTrap requires `Python`_ 2.6 or 2.7 and `MySQL`_ 5.1+ with the InnoDB
backend.

These steps assume that you have `git`_, `virtualenv`_, `virtualenvwrapper`_,
and a compilation toolchain available (with the `Python`_ and `MySQL`_ client
development header files), and that you have a local `MySQL`_ server running
which your shell user has permission to create databases in. See the full
:doc:`installation` documentation for details and troubleshooting.

1. ``git clone --recursive git://github.com/mozilla/moztrap``
2. ``cd moztrap``
3. ``mkvirtualenv moztrap``
4. ``bin/install-reqs``
5. ``echo "CREATE DATABASE moztrap CHARACTER SET utf8" | mysql``
6. ``./manage.py syncdb --migrate``
7. ``./manage.py create_default_roles``
8. ``./manage.py runserver``
9. Visit http://localhost:8000 in your browser.

Congratulations! If that all worked, you have a functioning instance of MozTrap
for local testing, experimentation, and :doc:`development <development>`.

Please read the :doc:`deployment` documentation for important security and
other considerations before deploying a public instance of MozTrap.

.. _git: http://git-scm.com
.. _Python: http://www.python.org
.. _MySQL: http://www.mysql.com
.. _virtualenv: http://www.virtualenv.org
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/


.. _detailed-install:

Detailed Install
----------------

First, clone the `MozTrap repository`_.

.. _MozTrap repository: https://github.com/mozilla/moztrap

Dependency source distribution tarballs are stored in a git submodule, so you
either need to clone with the ``--recursive`` option, or after cloning, from
the root of the clone, run::

    git submodule init; git submodule update

If you want to run the latest and greatest code, the default ``master`` branch
is what you want. If you want to run a stable release branch, switch to it now::

    git checkout 0.8.X


Install the Python dependencies
-------------------------------

If you want to run this project in a `virtualenv`_ to isolate it from other
Python projects on your system, create the virtualenv and activate it. Then run
``bin/install-reqs`` to install the dependencies for this project into your
Python environment.

.. Note::

    On some linux flavors, you may need to run
    ``sudo apt-get install libmysqlclient-dev`` prior to bin/install-reqs.

Installing the dependencies requires `pip`_ 1.0 or higher. `pip`_ is
automatically available in a `virtualenv`_; if not using `virtualenv`_ you may
need to install it yourself.

A few of MozTrap's dependencies include C code and must be
compiled. These requirements are listed in ``requirements/compiled.txt``. You
can either compile them yourself (the default option) or use pre-compiled
packages provided by your operating system vendor.


Compiling
~~~~~~~~~

By default, ``bin/install-reqs`` installs all dependencies, including several
that require compilation. This requires that you have a working compilation
toolchain (``apt-get install build-essential`` on Ubuntu, Xcode on OS X). It
also requires the Python development headers (``apt-get install python-dev`` on
Ubuntu) and the MySQL client development headers (``apt-get install
libmysqlclient-dev`` on Ubuntu).

If you are lacking the Python development headers, you will get the error
``Python.h: No such file or directory``. If you are lacking the MySQL client
development files, you will get an error that ``mysql_config`` cannot be found.


Using operating system packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer to use pre-compiled operating system vendor packages for the
compiled dependencies, you can avoid the need for the compilation toolchain and
header files. In that case, you need to install `MySQLdb`_, `py-bcrypt`_, and
`coverage`_ (the latter only if you want test coverage data) via operating
system packages (``apt-get install python-mysqldb python-bcrypt
python-coverage`` on Ubuntu).

If using a `virtualenv`_, you need to ensure that it is created with access to
the system packages. In `virtualenv`_ versions prior to 1.7 this was the
default, in recent versions use the ``--system-site-packages`` flag when
creating your `virtualenv`_.

Once you have the compiled requirements installed, install the rest of the
requirements using ``bin/install-reqs pure``; this installs only the
pure-Python requirements and doesn't attempt to compile the compiled
ones. Alternatively, you can skip ``bin/install-reqs`` entirely and use the
provided :ref:`vendor library`.


.. _virtualenv: http://www.virtualenv.org
.. _pip: http://www.pip-installer.org
.. _MySQLdb: http://pypi.python.org/pypi/python-mysqldb
.. _py-bcrypt: http://pypi.python.org/pypi/py-bcrypt
.. _coverage: http://nedbatchelder.com/code/coverage/



Create a database
-----------------

You'll need a MySQL database. If you have a local MySQL server and your user
has rights to create databases on it, just run this command to create the
database::

    echo "CREATE DATABASE moztrap CHARACTER SET utf8" | mysql

(If you are sure that UTF-8 is the default character set for your MySQL server,
you can just run ``mysqladmin create moztrap`` instead).

If you get an error here, your shell user may not have permissions to create a
MySQL database. In that case, you'll need to append ``-u someuser`` to the end
of that command, where ``someuser`` is a MySQL user who does have permission to
create databases (in many cases ``-u root`` will work). If you have to use
``-u`` to create the database, then before going on to step 5 you'll also need
to create a ``moztrap/settings/local.py`` file (copy the sample provided at
``moztrap/settings/local.sample.py``), and uncomment the ``DATABASES`` setting,
changing the ``USER`` key to the same username you passed to ``-u``.


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

You can access MozTrap in your browser at http://localhost:8000.

For a production deployment of MozTrap, please read the
:doc:`deployment` documentation for important security and other
considerations.

For notes on upgrading to a more recent MozTrap, see the
:doc:`upgrading` documentation.
