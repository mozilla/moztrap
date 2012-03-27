from django.conf.urls.defaults import patterns, url

from .views import Verify


urlpatterns = patterns(
    "",
    url("^browserid/verify/", Verify.as_view(), name="browserid_verify"),
)
