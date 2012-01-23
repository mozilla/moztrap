Case Conductor is a Test Case Management system.
Copyright (C) 2011-2012 Mozilla

This file is part of Case Conductor.

Case Conductor is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Case Conductor is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.

Case Conductor
==============

This is the Case Conductor test case management system.  It lives at
https://github.com/mozilla/caseconductor/.


Documentation
-------------

For more information about setting up, developing, and using Case Conductor,
see the documentation in the `docs/` directory.

To build and view an HTML version of the documentation::

    $ cd docs
    $ pip install sphinx
    $ make html
    $ firefox _build/index.html


Related repositories
--------------------

There are `Selenium`_ tests for Case Conductor in the `caseconductor-tests`_
repository.

Case Conductor's Python dependencies are available as sdist tarballs in the
`caseconductor-reqs`_ repository, and as an unpacked vendor library in the
`caseconductor-vendor-lib`_ repository. These are included as submodules of
this repository, at ``requirements/dist`` and ``requirements/vendor``
respectively.

.. _Selenium: http://seleniumhq.org
.. _caseconductor-tests: https://github.com/mozilla/caseconductor-tests
.. _caseconductor-reqs: https://github.com/mozilla/caseconductor-reqs
.. _caseconductor-vendor-lib: https://github.com/mozilla/caseconductor-vendor-lib
