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

    url("^manage/$", 
        "django.views.generic.simple.direct_to_template", 
        {"template": "manage/testcycle/cycles.html"}),
           
    url("^manage/testcase/add/$",
        "tcmui.testcases.views.add_testcase",
        name="add_testcase"),
)
