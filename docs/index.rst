Welcome to MozTrap
=========================

MozTrap is a test case manager.

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

Congratulations! If that all worked, you have a functioning instance of Case
Conductor for local testing, experimentation, and :doc:`development
<development>`.

Please read the :doc:`deployment` documentation for important security and
other considerations before deploying a public instance of MozTrap.

.. _git: http://git-scm.com
.. _Python: http://www.python.org
.. _MySQL: http://www.mysql.com
.. _virtualenv: http://www.virtualenv.org
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/


Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   upgrading
   development
   deployment
   userguide/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
