Upgrading
=========

To upgrade, simply use `git`_ to pull in the newer code from the `GitHub
repository`_ and update the submodules::

    git pull
    git submodule update

If you are on a stable release branch (e.g. ``0.8.X``) and you want to update
to a newer release branch (e.g. ``0.9.X``), make sure you've fetched the latest
code on all branches, switch to the branch you want, and update to the correct
version of the submodules for that branch::

    git fetch
    git checkout 0.9.X
    git submodule update


Updating dependencies
---------------------

Run ``git submodule update`` to get the latest version of the dependency
submodules, and then ``bin/install-reqs`` to install them into your
environment. Both of these commands are idempotent; there's no harm in running
them every time, whether there have been any dependency changes or not.

If you are using the :ref:`vendor library`, ``bin/install-reqs`` is not
necessary, the submodule update will get the latest version of the vendored
dependencies.


Database migrations
-------------------

It's possible that the changes you pulled in may have included one or more new
database migration scripts. To run any pending migrations::

    python manage.py syncdb --migrate

This command is idempotent, so there's no harm in running it after every
upgrade, whether it's necessary or not.

.. warning::

   It is possible that a database migration will include the creation of a new
   database table. If you've commented out the ``SET storage_engine=InnoDB``
   ``init_command`` in your ``cc/settings/local.py`` for performance reasons
   (see :ref:`database-performance-tweak`), you should uncomment it before
   running any migrations, to ensure that all new tables are created as
   ``InnoDB`` tables.


.. _git: http://git-scm.com
.. _GitHub repository: https://github.com/mozilla/caseconductor/
