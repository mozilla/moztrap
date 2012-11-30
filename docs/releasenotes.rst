Release Notes
=============

Version 1.3
-----------
* **Sharable list links** - When you have filtered a list somewhere in the
  system, you can click the *link* icon next to the filter field to
  bring up the url that you can share to show that list.  This link honors
  pagination and all filters.  And it can be used in the management area
  as well as results and in test runs.  This can be especially nice if you
  want to tell a tester to run a specific set of test cases in a run.
* **Test Run description while running tests** - We added the test run
  description field to the top of the page while running tests.  This
  field supports markdown, so you can put links and other instructions to
  your testers in there.  This can be especially helpful to add links to
  creating a new bug in your bugsystem of choice. (You **ARE** using
  Bugzilla, aren't you?) See :ref:`Run Edit Fields<test-run-edit-fields>` for
  more info.
* **Update active test runs** - The new *refresh* button in
  the management area will update an active run to newly added or removed
  test cases.  See :ref:`Refreshing a Run<test-run-refresh>` for more
  information.
* **Filtering performance** - In some screens, the auto-complete filters were
  being displayed for every keystroke.  Now they always wait till you're done
  typing before showing auto-complete options.


Version 1.2.7
-------------
* **Run activation scalability** - Using some new features in Django 1.4
  and a couple raw queries, we expanded support for test runs from ~700
  cases to several thousand.
* **Case import management command** - The feature for importing cases would
  prevent you from importing duplicates, even if you wanted to.  So added
  a param for that.  It also accepts a directory of several files instead
  of just a single file.


Version 1.2.5
-------------
* **Django 1.4.2 upgrade**
* **More non-ascii character fixes** - Primarily in some views and messages.
* **Split-the-work:** When you and others are executing the same test run,
  for the same environment, you'll see an icon on test cases where another
  tester has already submitted results.  You can still submit your own
  result if you choose, but this way you don't duplicate effort, if you
  don't want to.


Version 1.2
-------------
* **Test case ordering** - As you drag and drop cases in the edit Suite
  screen, that order will be honored when users run your tests.  Same goes
  for suites of test runs.  So, the order will be first by suite, then by
  case within the suite.  There is also a new field in the runtests area
  where, if you sorted by case name, you can re-sort by order, if you like.
* **Performance fix for editing large suites** - Scalability fix as thousands
  of cases had been entered into the system.
* **Run Series:** See :ref:`Test Run Series <test-run-series>` for more info on
  this new feature.
* **Better i18n support** - Added more support for non-ascii characters.
