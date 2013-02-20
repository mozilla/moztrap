"""
Tests for list actions.

"""
from mock import Mock

from django.http import HttpResponse
from django.test import RequestFactory

from tests import case



class ActionsTest(case.TestCase):
    """Tests for list-actions decorator."""
    @property
    def actions(self):
        """The decorator under test."""
        from moztrap.view.lists.actions import actions
        return actions


    def setUp(self):
        """Set up a mock Model class."""
        self.mock_model = Mock()


    def view(self, request, decorator=None):
        """
        Pass request to decorated test view, return response.

        Optionally accepts decorator to apply. Assigns request as ``request``
        attribute on response.

        """
        if decorator is None:
            decorator = self.actions(self.mock_model, ["doit"])

        @decorator
        def view(req):
            response = HttpResponse()
            response.request = req
            return response

        return view(request)


    def req(self, method, *args, **kwargs):
        """Shortcut for RequestFactory; adds request.user."""
        req = getattr(RequestFactory(), method)(*args, **kwargs)
        req.user = Mock()
        return req


    def test_uses_wraps(self):
        """Preserves docstring and name of original view func."""
        @self.actions("ctx_name", [])
        def myview(request, some_id):
            """docstring"""

        self.assertEqual(myview.func_name, "myview")
        self.assertEqual(myview.func_doc, "docstring")


    def test_passes_on_args(self):
        """Arguments are passed on to original view func."""
        record = []

        @self.actions("ctx_name", [])
        def myview(request, *args, **kwargs):
            record.extend([args, kwargs])

        myview(self.req("get", "/"), "a", b=2)

        self.assertEqual(record, [("a",), {"b": 2}])


    def test_action_redirects(self):
        """After action is taken, redirects to original URL."""
        req = self.req("post", "/the/url", data={"action-doit": "3"})

        res = self.view(req)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], "/the/url")


    def test_action_redirects_with_querystring(self):
        """Post-action redirect includes querystring."""
        req = self.req(
            "post", "/the/url?filter=value", data={"action-doit": "3"})

        res = self.view(req)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], "/the/url?filter=value")


    def test_ajax_no_redirect(self):
        """Ajax request doesn't redirect post-action."""
        req = self.req(
            "post", "/the/url?filter=value", data={"action-doit": "3"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        res = self.view(req)

        self.assertEqual(res.status_code, 200)


    def test_ajax_fall_through_method(self):
        """Post-action, ajax req continues with method GET and no POST data."""
        req = self.req(
            "post", "/the/url?filter=value", data={"action-doit": "3"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        res = self.view(req)

        self.assertEqual(res.request.method, "GET")
        self.assertEqual(res.request.POST, {})


    def test_action_called(self):
        """Correct method is called on correct object, with user."""
        req = self.req("post", "/the/url", data={"action-doit": "3"})
        req.user = Mock()

        self.view(req)

        model_get = self.mock_model._base_manager.get
        model_get.assert_called_with(pk="3")

        instance = model_get.return_value
        instance.doit.assert_called_with(user=req.user)


    def test_POST_no_action(self):
        """Without fallthrough, redirects even if no action taken."""
        req = self.req("post", "/the/url", data={})

        res = self.view(req)

        self.assertEqual(self.mock_model._base_manager.get.call_count, 0)
        self.assertEqual(res.status_code, 302)


    def test_bad_action(self):
        """Unknown action is handled the same as no action."""
        req = self.req("post", "/the/url", data={"action-bad": "3"})

        res = self.view(req)

        self.assertEqual(self.mock_model._base_manager.get.call_count, 0)
        self.assertEqual(res.status_code, 302)


    def test_fall_through(self):
        """If fall_through is set, POST falls through untouched if no action."""
        dec = self.actions(self.mock_model, ["doit"], fall_through=True)
        req = self.req("post", "/the/url", data={"other": "thing"})

        res = self.view(req, decorator=dec)

        self.assertEqual(self.mock_model._base_manager.get.call_count, 0)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.request.method, "POST")
        self.assertEqual(res.request.POST["other"], "thing")


    def test_object_does_not_exist(self):
        """If requested obj id does not exist, no action is taken."""
        req = self.req("post", "/the/url", data={"action-doit": "3"})

        class MockModelDoesNotExist(Exception):
            pass
        self.mock_model.DoesNotExist = MockModelDoesNotExist

        def raise_does_not_exist(*args, **kwargs):
            raise self.mock_model.DoesNotExist

        self.mock_model._base_manager.get.side_effect = raise_does_not_exist

        res = self.view(req)

        self.mock_model._base_manager.get.assert_called_with(pk="3")
        self.assertEqual(res.status_code, 302)


    def test_non_POST(self):
        """Decorator ignores non-POST requests."""
        req = self.req("get", "/the/url", data={"action-doit": "3"})

        self.view(req)

        self.assertEqual(self.mock_model._base_manager.get.call_count, 0)


    def test_no_permission(self):
        """If permission is passed in and user doesn't have it, returns 403."""
        req = self.req("post", "/the/url", data={"action-doit": "3"})
        req.user = Mock()
        req.user.has_perm.return_value = False

        res = self.view(
            req,
            decorator=self.actions(
                self.mock_model, ["doit"], permission="do_things")
            )

        self.assertEqual(res.status_code, 403)
        req.user.has_perm.assert_called_with("do_things")


    def test_has_permission(self):
        """If permission is passed in and user has it, success."""
        req = self.req("post", "/the/url", data={"action-doit": "3"})
        req.user = Mock()
        req.user.has_perm.return_value = True

        res = self.view(
            req,
            decorator=self.actions(
                self.mock_model, ["doit"], permission="do_things")
            )

        self.assertEqual(res.status_code, 302)
        req.user.has_perm.assert_called_with("do_things")
