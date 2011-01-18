from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns(
    "",
    url("^$", direct_to_template, {"template": "home.html"}, name="home"),
    url("^account/register/$", direct_to_template, {"template": "account/register.html"}, name="register"),
    url("^test/$", direct_to_template, {"template": "test/products.html"}, name="products"),
    url("^test/product/1/environment/$", direct_to_template, {"template": "test/environment.html"}, name="environment"),
    url("^test/product/1/cycles/$", direct_to_template, {"template": "test/cycles.html"}, name="cycles"),
    url("^test/product/1/cycles/1/$", direct_to_template, {"template": "test/run.html"}, name="run"),
    url("^manage/testcase/add/$", direct_to_template, {"template": "test/add_case.html"}, name="add"),
)
