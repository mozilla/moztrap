from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "tcmui.manage.views",
    url("^$", "home", name="manage"),

    # test cycles
    url("^testcycles/$", "testcycles", name="manage_testcycles"),
)

urlpatterns += patterns(
    "",
    url("^testcycle/add/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "manage/testcycle/add_cycle.html"},
        name="manage_testcycle_add"),

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
