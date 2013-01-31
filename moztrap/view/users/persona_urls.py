from django.conf.urls.defaults import patterns, url

from .views import Verify


urlpatterns = patterns(
    "",
    url("^persona/verify/", Verify.as_view(), name="persona_verify"),
)
