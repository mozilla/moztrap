"""
Account-related URLs.

"""
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from session_csrf import anonymous_csrf

from . import views


urlpatterns = patterns(
    "moztrap.view.users.views",

    # auth -------------------------------------------------------------------

    url(r"^login/", "login", name="auth_login"),
    url(r"^logout/", "logout", name="auth_logout"),
    url(r"^password/change/$", "password_change", name="auth_password_change"),
    url(r"^password/reset/$", "password_reset", name="auth_password_reset"),
    url(r"^reset/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        "password_reset_confirm",
        name="auth_password_reset_confirm"),
    url(r"^set_name/$", "set_username", name="auth_set_username"),
    url(r"^(?P<user_id>\d+)/apikey/$", "create_apikey", name="auth_create_apikey"),

    # registration -----------------------------------------------------------

    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r"^activate/(?P<activation_key>\w+)/$",
        anonymous_csrf(views.ActivationView.as_view()),
        name="registration_activate"),
    url(r"^register/$",
        anonymous_csrf(views.RegistrationView.as_view()),
        name="registration_register"),
    url(r"^register/closed/$",
        TemplateView.as_view(template_name="users/registration_closed.html"),
        name="registration_disallowed"),
    )
