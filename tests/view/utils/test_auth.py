"""
Tests for auth view utilities.

"""
from django.http import HttpResponse
from django.test import RequestFactory

from django.contrib.auth.models import AnonymousUser

from django.test.utils import override_settings
from tests import case



class AjaxTest(case.TestCase):
    @property
    def login_maybe_required(self):
        """The decorator-factory under test."""
        from moztrap.view.utils.auth import login_maybe_required
        return login_maybe_required


    @property
    def view(self):
        """A simple view, decorated with @login_maybe_required."""
        @self.login_maybe_required
        def view(request):
            return HttpResponse("success")

        return view


    @override_settings(ALLOW_ANONYMOUS_ACCESS=False)
    def test_no_anonymous(self):
        """With no anonymous access, decorator requires login."""
        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        response = self.view(request)
        self.assertEqual(response.status_code, 302)


    @override_settings(ALLOW_ANONYMOUS_ACCESS=True)
    def test_anonymous(self):
        """With anonymous access allowed, decorator is no-op."""
        request = RequestFactory().get("/")
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "success")
