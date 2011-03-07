from django.conf.urls.defaults import patterns, url, include



urlpatterns = patterns(
    "",
    url("^$", "tcmui.products.views.product_list", name="products"),
    url("^account/", include("tcmui.users.urls")),
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
    
    # management wireframes direct-to-template
    url("^manage/$", 
        "django.views.generic.simple.direct_to_template", 
        {"template": "manage/testcycle/cycles.html"}),
    # testcycles direct-to-template
    url("^manage/testcycles/$", 
        "django.views.generic.simple.direct_to_template", 
        {"template": "manage/testcycle/cycles.html"}),
    url("^manage/testcycle/add/$", 
        "django.views.generic.simple.direct_to_template", 
        {"template": "manage/testcycle/add_cycle.html"}),
    # testruns direct-to-template
    url("^manage/testruns/$", 
        "django.views.generic.simple.direct_to_template", 
        {"template": "manage/testrun/runs.html"}),
    url("^manage/testrun/add/$", 
        "django.views.generic.simple.direct_to_template", 
        {"template": "manage/testrun/add_run.html"}),
    # testcases direct-to-template
    url("^manage/testcases/$", 
        "django.views.generic.simple.direct_to_template", 
        {"template": "manage/testcase/cases.html"}),

    # add testcase wireframe is live
    url("^manage/testcase/add/$",
        "tcmui.testcases.views.add_testcase",
        name="add_testcase"),
)
