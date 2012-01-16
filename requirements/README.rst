Requirements files
==================

pure.txt
   The pure-Python core dependencies of Case Conductor.

compiled.txt
   The compiled core dependencies of Case Conductor.

dev.txt
   Full requirements suitable for developing Case Conductor; includes both
   ``pure.txt`` and ``compiled.txt`` as well as a number of other
   development-only dependencies (some of which are pure-Python and some of
   which are compiled).  This is the requirements file used by
   ``bin/install-reqs`` by default.

prod-base.txt
   Dependencies needed only for a production/staging deployment.

prod.txt
   Full requirements for a production/staging deployment: includes
   ``pure.txt``, ``compiled.txt``, and ``prod-base.txt``.

prod-pure.txt
   Full pure-Python requirements for a production/staging deployment;
   includes ``pure.txt`` and ``prod-base.txt``. This is the requirements
   file used to generate the bundled vendor library in
   ``requirements/vendor``. The dependencies in ``compiled.txt`` must be
   installed at the OS level.

gems.txt
   Ruby gems necessary to regenerate CSS from modified Sass files; used by
   ``bin/install-gems``.
