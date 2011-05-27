"""
Tests for core TCM decorators.

"""
from unittest2 import TestCase
from mock import patch

from django.template.response import TemplateResponse
from django.test import RequestFactory

from ..responses import response, make_identity
from ..utils import TestResourceTestCase



class TemplateResponseDecoratorTestCase(TestResourceTestCase):
    """
    Utilities for testing view decorators intended for application on views
    that usually return a TemplateResponse.

    """
    @property
    def factory(self):
        """
        Should return the factory function for the decorator under test.

        """
        raise NotImplementedError


    factory_args = ()


    @property
    def decorator(self):
        """
        Should return an actual decorator (simplest case arguments provided to
        factory function).

        """
        return self.factory(*self.factory_args)


    def req(self, method="GET", path="/some/url", *args, **kwargs):
        req = getattr(RequestFactory(), method.lower())(path, *args, **kwargs)
        req.auth = self.auth
        return req


    def on_response(self, response, decorator=None, request=None):
        """
        For decorators that only care about the response, not the request;
        applies the given decorator to a dummy view function that returns the
        given response, and returns the resulting response.

        """
        decorator = decorator or self.decorator
        request = request or self.req()

        @decorator
        def view(request):
            return response

        return view(request)


    def on_template_response(self, context, **kwargs):
        """
        Given a context, runs a TemplateResponse with that context through the
        decorated view.

        """
        request = kwargs.setdefault("request", self.req())

        res = TemplateResponse(request, "some/template.html", context)

        return self.on_response(res, **kwargs)



class TemplateResponseDecoratorBaseTests(object):
    """
    Common tests for template response decorators.

    """
    def test_returns_non_template_response(self):
        """
        The decorator returns a non-TemplateResponse unmodified, without error.

        """
        res = self.on_response("blah")

        self.assertEqual(res, "blah")


    def test_uses_wraps(self):
        @self.decorator
        def myview(request, some_id):
            """docstring"""

        self.assertEqual(myview.func_name, "myview")
        self.assertEqual(myview.func_doc, "docstring")


    def test_passes_on_args(self):
        record = []

        @self.decorator
        def myview(request, *args, **kwargs):
            record.extend([args, kwargs])

        myview(self.req(), "a", b=2)

        self.assertEqual(record, [("a",), {"b": 2}])



class ListDecoratorBaseTests(TemplateResponseDecoratorBaseTests):
    """
    Common tests for decorators whose factory function first argument specifies
    a template context name in which a ListObject subclass instance is found
    that the decorator operates on.

    """
    @property
    def ctx_name(self):
        raise NotImplementedError


    def on_listobject_response(self, res=None, **kwargs):
        res = res or response(self.builder.searchresult({}))

        with patch("tcmui.core.api.userAgent") as http:
            http.request.return_value = res
            lst = self.resource_list_class.get()
            res = self.on_template_response({self.ctx_name: lst}, **kwargs)

        return res


    def test_does_not_deliver_listobject(self):
        res = self.on_listobject_response()
        self.assertFalse(res.context_data[self.ctx_name]._delivered)



class ListCtxDecoratorBaseTests(ListDecoratorBaseTests):
    """
    Common tests for decorators whose factory function first argument specifies
    a template context name in which a ListObject subclass instance is found
    that the decorator operates on.

    """
    @property
    def ctx_name(self):
        return self.factory_args[0]



class SortTest(ListCtxDecoratorBaseTests,
               TemplateResponseDecoratorTestCase):
    @property
    def factory(self):
        from tcmui.core.decorators import sort
        return sort


    factory_args = ("ctx_name",)


    @patch("tcmui.core.decorators.sort_util.Sort")
    def test_sort_initialization(self, sort_class):
        req = self.req(
            "GET", "/a/url", {"sortfield": "name", "sortdirection": "desc"})
        self.on_listobject_response(request=req)

        sort_class.assert_called_with(
            '/a/url?sortfield=name&sortdirection=desc', 'name', 'desc')


    @patch("tcmui.core.decorators.sort_util.Sort")
    def test_no_sort(self, sort_class):
        self.on_listobject_response()

        sort_class.assert_called_with('/some/url', None, 'asc')


    @patch("tcmui.core.decorators.sort_util.Sort")
    def test_sort_defaults(self, sort_class):
        dec = self.factory(
            *self.factory_args, defaultfield="name", defaultdirection="desc")
        self.on_listobject_response(decorator=dec)

        sort_class.assert_called_with('/some/url', 'name', 'desc')


    @patch("tcmui.core.decorators.sort_util.Sort")
    def test_sort_object_in_context(self, sort_class):
        req = self.req(
            "GET", "/a/url", {"sortfield": "name", "sortdirection": "desc"})
        res = self.on_listobject_response(request=req)

        self.assertEqual(res.context_data["sort"], sort_class.return_value)



    @patch("tcmui.core.decorators.sort_util.Sort")
    def test_listobj_sorted(self, sort_class):
        req = self.req(
            "GET", "/a/url", {"sortfield": "name", "sortdirection": "desc"})
        res = self.on_listobject_response(request=req)

        lst = res.context_data[self.ctx_name]
        self.assertEqual(
            lst._location, "testresources?sortfield=name&sortdirection=desc")



class FilterTest(ListCtxDecoratorBaseTests,
                 TemplateResponseDecoratorTestCase):
    @property
    def factory(self):
        from tcmui.core.decorators import filter
        return filter


    factory_args = ("ctx_name",)


    @patch("tcmui.core.decorators.filters.Filter")
    def test_filter_initialization(self, filter_class):
        self.on_listobject_response()

        from django.http import QueryDict
        filter_class.assert_called_with(QueryDict({}), self.auth)


    @patch("tcmui.core.decorators.filters.Filter")
    def test_filter_method_args(self, filter_class):
        res = self.on_listobject_response()

        flt = res.context_data["filter"]
        self.assertIsInstance(
            flt.filter.call_args[0][0], self.resource_list_class)


    @patch("tcmui.core.decorators.filters.Filter")
    def test_filter_return_value_assigned(self, filter_class):
        res = self.on_listobject_response()

        flt = res.context_data["filter"]
        self.assertEqual(
            flt.filter.return_value, res.context_data[self.ctx_name])


    @patch("tcmui.core.decorators.filters.Filter")
    def test_fields_passed_to_filter(self, filter_class):
        dec = self.factory(*(self.factory_args + ("a", "b")))
        self.on_listobject_response(decorator=dec)

        from django.http import QueryDict
        filter_class.assert_called_with(QueryDict({}), self.auth, "a", "b")



class PaginateTest(ListCtxDecoratorBaseTests,
                   TemplateResponseDecoratorTestCase):
    @property
    def factory(self):
        from tcmui.core.decorators import paginate
        return paginate


    factory_args = ("ctx_name",)

    def test_pager(self):
        res = self.on_listobject_response()

        pager = res.context_data["pager"]
        self.assertEqual(pager.total, 1)



class ActionsTest(ListDecoratorBaseTests, TemplateResponseDecoratorTestCase):
    @property
    def factory(self):
        from tcmui.core.decorators import actions
        return actions


    ctx_name = "lst"


    def setUp(self):
        self.doit_ids = []
        # patch a simple action method onto the test resource class
        def doit(self_):
            self.doit_ids.append(self_.id)
        self.resource_class.doit = doit


    @property
    def factory_args(self):
        return (self.resource_list_class, ["doit"])


    def test_action_redirects(self):
        req = self.req("POST", "/the/url", data={"action-doit": "3"})
        res = self.on_listobject_response(
            response(self.builder.one(resourceIdentity=make_identity(id=3))),
            request=req)

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], "/the/url")


    def test_action_called(self):
        req = self.req("POST", "/the/url", data={"action-doit": "3"})
        self.on_listobject_response(
            response(self.builder.one(resourceIdentity=make_identity(id=3))),
            request=req)

        self.assertEqual(self.doit_ids, [u"3"])


    def test_POST_no_action(self):
        req = self.req("POST", "/the/url", data={})
        res = self.on_listobject_response(request=req)

        self.assertEqual(self.doit_ids, [])
        self.assertEqual(res.status_code, 302)


    def test_bad_action(self):
        req = self.req("POST", "/the/url", data={"action-bad": "3"})
        res = self.on_listobject_response(request=req)

        self.assertEqual(self.doit_ids, [])
        self.assertEqual(res.status_code, 302)


    def test_fall_through(self):
        dec = self.factory(*self.factory_args, fall_through=True)
        req = self.req("POST", "/the/url", data={})
        res = self.on_listobject_response(request=req, decorator=dec)

        self.assertEqual(self.doit_ids, [])
        self.assertEqual(res.status_code, 200)


    @patch("tcmui.core.decorators.errors.error_message")
    @patch("tcmui.core.decorators.messages.error")
    def test_conflict(self, error, error_message):
        exc = self.resource_class.Conflict("conflict!")
        def doit(self_):
            raise exc

        error_message.return_value = "an error message"
        with patch.object(self.resource_class, "doit", doit):
            req = self.req("POST", "/the/url", data={"action-doit": "3"})
            res = self.on_listobject_response(request=req)

        self.assertEqual(res.status_code, 302)
        error.assert_called_with(req, "an error message")
        self.assertIsInstance(error_message.call_args[0][0], self.resource_class)
        self.assertEqual(error_message.call_args[0][1], exc)




class AsAdminTest(TestCase):
    @property
    def cls(self):
        from tcmui.core.decorators import as_admin

        class TestObject(object):
            def __init__(self):
                self.auth = ["original auth"]
                self.call_args_list = []
                self.auth_list = []

            @as_admin
            def a_method(self, *args, **kwargs):
                self.call_args_list.append((args, kwargs))
                self.auth_list.append(self.auth)

        return TestObject


    def test_uses_admin_auth(self):
        from tcmui.core.auth import admin

        obj = self.cls()
        obj.a_method()

        self.assertIs(obj.auth_list[-1], admin)


    def test_restores_previous_auth(self):
        obj = self.cls()

        prev = obj.auth

        obj.a_method()

        self.assertIs(obj.auth, prev)


    def test_passes_on_all_args(self):
        obj = self.cls()

        obj.a_method(1, 2, a=1, b=2)

        self.assertEqual(obj.call_args_list[-1], ((1, 2), {"a": 1, "b": 2}))
