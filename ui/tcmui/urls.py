from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns(
    "",
    url("^$", direct_to_template, {"template": "home.html"}, name="home"),
    url("^account/register/$", direct_to_template, {"template": "account/register.html"}, name="register"),
    url("^test/products/$", direct_to_template, {"template": "test/products.html"}, name="products"),
    url("^test/product/firefox/environment/$", direct_to_template, {"template": "test/environment.html"}, name="environment"),
    url("^test/product/firefox/cycles/$", direct_to_template, {"template": "test/cycles.html"}, name="cycles"),
    url("^test/product/firefox/cycles/1/$", direct_to_template, {"template": "test/run.html"}, name="run"),
)
