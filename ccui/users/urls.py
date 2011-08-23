from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    "ccui.users.views",
    url("^register/$", "register", name="register"),
    url("^login/$", "login", name="login"),
    url("^logout/$", "logout", name="logout"),
    )
