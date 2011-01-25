from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    "tcmui.users.views",
    url("^register/$", "register", name="register"),
    )
