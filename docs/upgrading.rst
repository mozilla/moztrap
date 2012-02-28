Upgrading
=========

To upgrade, simply use `git`_ to pull in the newer code from the `GitHub
repository`_::

    git pull

If you are on a stable release branch (e.g. ``0.8.X``) and you want to update
to a newer release branch (e.g. ``0.9.X``), make sure you've fetched the latest
code on all branches and then switch to the branch you want::

    git fetch
    git checkout 0.9.X


Database migrations
-------------------

It's possible that the changes you pulled in may have included one or more new
database migration scripts. To run any pending migrations::

    python manage.py syncdb --migrate


.. _git: http://git-scm.com
.. _GitHub repository: https://github.com/mozilla/caseconductor/
