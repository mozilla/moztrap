from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "tcmui.manage.views",
    url("^$", "home", name="manage"),

    # test cycles
    url("^testcycles/$", "testcycles", name="manage_testcycles"),
    url("^testcycle/add/$", "add_testcycle", name="manage_testcycle_add"),
    url("^testcycle/(?P<cycle_id>\d+)/$", "edit_testcycle", name="manage_testcycle_edit"),
)

urlpatterns += patterns(
    "",
    # testruns direct-to-template
    url("^testruns/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "manage/testrun/runs.html"}),
    url("^testrun/add/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "manage/testrun/add_run.html"}),

    # testsuites direct-to-template
    url("^testsuites/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "manage/testsuite/suites.html"}),
    url("^testsuite/add/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "manage/testsuite/add_suite.html"}),

    # testcases direct-to-template
    url("^testcases/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "manage/testcase/cases.html"}),
)


urlpatterns += patterns(
    "",
    url("^testcase/add/$",
        "tcmui.testcases.views.add_testcase",
        name="manage_testcase_add"),
)
