TCM UI
======

This Django project is the user interface to the new Mozilla/uTest TCM. It
lives at https://github.com/mozilla/tcm/, and is built to speak to the backend
API at https://github.com/mozilla/tcmplatform.

Development
-----------

First, update git submodules (dependency source distribution tarballs are
stored in a git submodule). From the root of this repo, run::

    git submodule init; git submodule update

Then run ``bin/install-reqs`` to install the dependencies for this project into
your Python environment (you may want to make this a `virtualenv`_ to isolate
it from other Python projects on your system).

At this point, you should be able to run ``./manage.py runserver`` and access
the UI in your browser at ``http://localhost:8000``.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv
