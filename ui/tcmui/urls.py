from django.conf.urls.defaults import patterns, url, include



urlpatterns = patterns(
    "",
    url("^$", "tcmui.products.views.product_list", name="products"),
    url("^account/", include("tcmui.users.urls")),

    # run tests
    url("^environment/$",
        "tcmui.environments.views.set_environment",
        name="environment"),
    url("^product/(?P<product_id>\d+)/cycles/$",
        "tcmui.testexecution.views.cycles",
        name="cycles"),
    url("^cycle/(?P<cycle_id>\d+)/$",
        "tcmui.testexecution.views.testruns",
        name="testruns"),
    url("^run/(?P<testrun_id>\d+)/$",
        "tcmui.testexecution.views.runtests",
        name="runtests"),
    url("^result/(?P<result_id>\d+)/$",
        "tcmui.testexecution.views.result",
        name="result"),

    # manage
    url("^manage/", include("tcmui.manage.urls")),

    # results (wireframed)
    url(r"^results/testcycles/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "results/testcycle/cycles.html"}),
    url(r"^results/testruns/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "results/testrun/runs.html"}),
    url(r"^results/testsuites/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "results/testsuite/suites.html"}),
    url(r"^results/testcases/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "results/testcase/cases.html"}),
    url(r"^results/testcase/detail/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "results/testcase/included_case_detail.html"}),

    # new runtest nav (wireframed)
    url(r"^wire/run/$",
        "django.views.generic.simple.direct_to_template",
        {"template": "test/wireframe.html"}),
)
