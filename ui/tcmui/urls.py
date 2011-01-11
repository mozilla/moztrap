from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns(
    "",
    url("^$", direct_to_template, {"template": "home.html"}, name="home"),
    url("^account/register/$", direct_to_template, {"template": "account/register.html"}, name="register"),
)
