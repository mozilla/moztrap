Release Notes
=============


Version 1.4.5
-------------
*release date - 3/28/2013*

* **Upgrade to Django 1.4.5**
* **Bug fix for order of cases** - Test case order within suites was broken.
* **Bug fix for repeated cases** - It was possible, in some circumstances to
  have the same test case shown multiple times in a suite.


Version 1.4.4
-------------
*release date - 3/22/2013*

* **Link to view result while running test** - If you want to share the result
  you just found with someone, clicking the result icon (like passed / failed)
  will navigate you to the result for that test.  You can then share that link
  or add it to a bug, etc.
* **Case name sync** - It ends up that having unique case names for different
  versions of the case is confusing.  This is especially true when you are
  selecting cases for a suite.  The screen must show you one of the case names
  so it shows you the latest case name.  This may not be the one you're
  thinking of if you're working on an earlier product.  So to simplify this,
  any time you save a case, it will make all the version of that case the same.
* **Several bug fixes** - please see Pivotal Tracker_ for details.


Version 1.4
-----------
*release date - 1/22/2013*

* **Fill Product Version Cases** - Added the ability to fill in case versions
  when they exist in one product version and not in another.  This can be handy
  if you have created version 1.0 and 2.0 of your product in MozTrap, and have
  been adding new cases to 1.0 as you go.  When it's time for 2.0, you want
  all those new cases to get moved forward.  In this case, edit the 2.0
  Product Version to fill cases from 1.0.
  See :ref:`Fill Case Versions<product-version-fill-cases>` for more info.
* **Mass Tag / Untag Cases** - If you want to add a new tag to lots of cases,
  you previously had to edit each case and add it.  Now, if you edit the tag
  in question, and select the product for the cases, you will see a list of
  available and included cases for that tag.  This makes it possible to
  :ref:`merge tags<tag-merge>`.  See :ref:`Tags<tags>` for info.
* **Filter results by status** - You can now filter results cases by passed,
  failed or invalidated.
* **Page title shows location** - You can no see where in the product you are
  by the page / tab title.
* **other tweaks and bug fixes**


Version 1.3.5
-------------
*release date - 12/19/2012*

* **Pinned Filters** - This feature allows you to **pin** a filter so that it
  remains constant for the session.  This way, if you want to only see data
  for a particular :ref:`product<products>` then you can pin the filter for it
  and everywhere you go, you only see data for that product.  For more info,
  see :ref:`pinned filters<pinned-filters>`.
* **See test results from other users** - There has been an icon while running
  tests that indicates that another user has run it, and what that result is.
  And with this release, we added the comment from failed or invalid tests to
  the rollover text.  In addition, this is now a button that will take you to
  the results details for that test case.  See
  :ref:`Results of others<other-results>` for more info.
* **Edit cases while running** - If you notice that a case needs updating while
  you are running it, there is now an *Edit this case* link in the upper right
  that will open a new tab to edit the contents of the case.  See
  :ref:`running tests<runtests>` for more info.
* **minor bug fixes** - New run series member sets start date to today, rather
  than that of the series itself.  Creating a case, setting suite adds the case
  to the end of the suite order.


Version 1.3.2
-------------
*release date - 12/18/2012*

* **Tag Descriptions** - You can now add descriptions to tags.  The result is
  that when you execute tests, the description is displayed for each case
  that has that tag.  This is a handy way to make notes that apply to a group
  of cases, like preconditions, links, etc.  As always, Markdown_ syntax is
  suported.  See :ref:`Tags<tags>` for more info.
* **Fixed refresh run bug** - The :ref:`test run refresh<test-run-refresh>`
  to get newly added cases was broken.  Now fixed.


Version 1.3.1
-------------
*release date - 12/10/2012*

* **Display all case versions** - Formerly, when you looked at the
  ``manage | cases`` area, you would only see the latest version of each test
  case, unless you were filtering for a different version.  This was confusing
  to many users, so now you see each distinct case version.
* **Delete distinct case versions** - Fixed where deleting one case version
  deleted all of them.
* **Create case no version default** - Many users were accidentally creating
  new cases for the latest version, when they meant to create it for an earlier
  version.  Since the default for new cases is the latest version, this went
  un-noticed a lot.  Removing the default makes it more deliberate.


Version 1.3
-----------
*release date - 12/03/2012*

* **Sharable list links** - When you have filtered a list somewhere in the
  system, you can click the *link* icon next to the filter field to
  bring up the url that you can share to show that list.  This link honors
  pagination and all filters.  And it can be used in the management area
  as well as results and in test runs.  This can be especially nice if you
  want to tell a tester to run a specific set of test cases in a run.
  See :ref:`Sharing Filters<share-filters>` for more info.
* **Test Run description while running tests** - We added the test run
  description field to the top of the page while running tests.  This
  field supports markdown, so you can put links and other instructions to
  your testers in there.  This can be especially helpful to add links to
  creating a new bug in your bugsystem of choice. (You **ARE** using
  Bugzilla, aren't you?) See :ref:`Run Edit Fields<test-run-edit-fields>` for
  more info.
* **Filtering performance** - In some screens, the auto-complete filters were
  being displayed for every keystroke.  Now they always wait till you're done
  typing before showing auto-complete options.


Version 1.2.7
-------------
* **Run activation scalability** - Using some new features in Django 1.4
  and a couple raw queries, we expanded support for test runs from ~700
  cases to several thousand.
* **Update active test runs** - The new *refresh* button in
  the management area will update an active run to newly added or removed
  test cases.  See :ref:`Refreshing a Run<test-run-refresh>` for more
  information.
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

.. _Markdown: http://daringfireball.net/projects/markdown/syntax
.. _Tracker: https://www.pivotaltracker.com/projects/280483#
