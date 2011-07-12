from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template


urlpatterns = patterns(
    "tcmui.manage.views",
    url("^$", "home", name="manage"),

    # test cycles
    url("^testcycles/$", "testcycles", name="manage_testcycles"),
    url("^testcycles/_detail/(?P<cycle_id>\d+)/$",
        "testcycle_details",
        name="manage_testcycle_details"),
    url("^testcycle/add/$", "add_testcycle", name="manage_testcycle_add"),
    url("^testcycle/(?P<cycle_id>\d+)/$", "edit_testcycle", name="manage_testcycle_edit"),

    # test runs
    url("^testruns/$", "testruns", name="manage_testruns"),
    url("^testruns/_detail/(?P<run_id>\d+)/$",
        "testrun_details",
        name="manage_testrun_details"),
    url("^testrun/add/$", "add_testrun", name="manage_testrun_add"),
    url("^testrun/(?P<run_id>\d+)/$", "edit_testrun", name="manage_testrun_edit"),

    # test suites
    url("^testsuites/$", "testsuites", name="manage_testsuites"),
    url("^testsuites/_detail/(?P<suite_id>\d+)/$",
        "testsuite_details",
        name="manage_testsuite_details"),
    url("^testsuite/add/$", "add_testsuite", name="manage_testsuite_add"),
    url("^testsuite/(?P<suite_id>\d+)/$", "edit_testsuite", name="manage_testsuite_edit"),

    # test cases
    url("^testcases/$", "testcases", name="manage_testcases"),
    url("^testcases/_detail/(?P<case_id>\d+)/$",
        "testcase_details",
        name="manage_testcase_details"),
    url("^testcase/add/$", "add_testcase", name="manage_testcase_add"),
    url("^testcase/(?P<case_id>\d+)/$", "edit_testcase", name="manage_testcase_edit"),

    # environment profile list (wireframed)
    url(r"^environments/$", direct_to_template,
        {"template": "manage/environment/profiles.html"}),
    # environment profile create (wireframed)
    url(r"^environment/add/$", direct_to_template,
        {"template": "manage/environment/add_profile.html"}),
    # environment profile create (wireframed)
    url(r"^environment/edit/$", direct_to_template,
        {"template": "manage/environment/edit_profile.html"}),
    # environment narrowing (wireframed)
    url(r"^type/id/environments/$", direct_to_template,
        {"template": "manage/environment/narrowing.html"}),

)
