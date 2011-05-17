from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template



urlpatterns = patterns(
    "tcmui.results.views",
    url("^$", "home", name="results"),

    url(r"^testcycles/$", "testcycles", name="results_testcycles"),
    url(r"^testruns/$", "testruns", name="results_testruns"),

    url(r"^testsuites/$",
        direct_to_template,
        {"template": "results/testsuite/suites.html"},
        name="results_testsuites"),
    url(r"^testcases/$",
        direct_to_template,
        {"template": "results/testcase/cases.html"},
        name="results_testcases"),
    url(r"^testcase/detail/$",
        direct_to_template,
        {"template": "results/testcase/included_case_detail.html"},
        name="results_testresults"),
)
