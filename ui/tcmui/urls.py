from django.conf.urls.defaults import patterns, url, include
from django.views.generic.simple import direct_to_template


urlpatterns = patterns(
    "",
    url("^account/", include("tcmui.users.urls")),

    url("^$", direct_to_template, {"template": "test/products.html"}, name="products"),
    url("^product/1/environment/$", direct_to_template, {"template": "test/environment.html"}, name="environment"),
    url("^product/1/cycles/$", direct_to_template, {"template": "test/cycles.html"}, name="cycles"),
    url("^product/1/cycles/1/$", direct_to_template, {"template": "test/run.html"}, name="run"),
    url("^manage/testcase/add/$", direct_to_template, {"template": "test/add_case.html"}, name="add"),
)
