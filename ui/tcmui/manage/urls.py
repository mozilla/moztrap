from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "tcmui.manage.views",
    url("^$", "home", name="manage"),

    # test cycles
    url("^testcycles/$", "testcycles", name="manage_testcycles"),
    url("^testcycle/add/$", "add_testcycle", name="manage_testcycle_add"),
    url("^testcycle/(?P<cycle_id>\d+)/$", "edit_testcycle", name="manage_testcycle_edit"),

    # test runs
    url("^testruns/$", "testruns", name="manage_testruns"),
    url("^testrun/add/$", "add_testrun", name="manage_testrun_add"),
    url("^testrun/(?P<run_id>\d+)/$", "edit_testrun", name="manage_testrun_edit"),

    # test suites
    url("^testsuites/$", "testsuites", name="manage_testsuites"),
    url("^testsuite/add/$", "add_testsuite", name="manage_testsuite_add"),
    url("^testsuite/(?P<suite_id>\d+)/$", "edit_testsuite", name="manage_testsuite_edit"),

    # test cases
    url("^testcases/$", "testcases", name="manage_testcases"),
    url("^testcase/add/$", "add_testcase", name="manage_testcase_add"),
    url("^testcase/(?P<case_id>\d+)/$", "edit_testcase", name="manage_testcase_edit"),
)

