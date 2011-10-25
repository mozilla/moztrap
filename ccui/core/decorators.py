from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect, render

from . import pagination, filters, errors, sort as sort_util
from .auth import admin
from .util import get_action



def sort(ctx_name, defaultfield=None, defaultdirection=sort_util.DEFAULT):
    """
    View decorator that handles sorting of a ListObject. Expects to find it
    in the TemplateResponse context under the name ``ctx_name``.

    This needs to not force delivery of the ListObject.

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            try:
                ctx = response.context_data
            except AttributeError:
                return response
            field, direction = sort_util.from_request(
                request, defaultfield, defaultdirection)
            ctx[ctx_name] = ctx[ctx_name].sort(field, direction)
            ctx["sort"] = sort_util.Sort(
                request.get_full_path(), field, direction)
            return response

        return _wrapped_view

    return decorator



def filter(ctx_name, *fields):
    """
    View decorator that handles filtering of a ListObject. Expects to find it
    in the TemplateResponse context under the name ``ctx_name``.

    This needs to not force delivery of the ListObject.

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            try:
                ctx = response.context_data
            except AttributeError:
                return response
            flt = filters.Filter(
                request.GET,
                request.auth,
                *fields)
            ctx[ctx_name] = flt.filter(ctx[ctx_name])
            ctx["filter"] = flt
            return response

        return _wrapped_view

    return decorator



def paginate(ctx_name):
    """
    View decorator that handles pagination of a ListObject. Expects to find it
    in the TemplateResponse context under the name ``ctx_name``.

    This needs to not force delivery of the ListObject.

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            try:
                ctx = response.context_data
            except AttributeError:
                return response
            pagesize, pagenum = pagination.from_request(request)
            ctx[ctx_name] = ctx[ctx_name].paginate(pagesize, pagenum)
            # the lambda here makes Pager fetch the total result count
            # lazily; another decorator might modify the result set yet.
            total = lambda: ctx[ctx_name].totalResults
            ctx["pager"] = pagination.Pager(total, pagesize, pagenum)
            return response

        return _wrapped_view

    return decorator



def actions(list_model, allowed_actions, fall_through=False):
    """
    View decorator that handles any POST keys named "action-method", where
    "method" must be in ``allowed_actions``. The value of the key should be an
    ID of ``list_model``, and "method" will be called on it, with any errors
    handled.

    By default, any "POST" request will be redirected back to the same URL
    (unless it's an AJAX request, in which case it sets the request method to
    GET and clears POST data, which has a similar effect without actually doing
    a redirect). If ``fall_through`` is set to True, the redirect/method-switch
    will only occur if an action was found in the POST data (allowing this
    decorator to be used with views that also do normal non-actions form
    handling.)

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method == "POST":
                action_taken = False
                action_data = get_action(request.POST)
                if action_data:
                    action, obj_id = action_data
                    if action in allowed_actions:
                        obj = list_model.get_by_id(obj_id, auth=request.auth)
                        try:
                            getattr(obj, action)()
                        except obj.Conflict, e:
                            messages.error(
                                request, errors.error_message(obj, e))
                        action_taken = True
                if action_taken or not fall_through:
                    if request.is_ajax():
                        request.method = "GET"
                        request.POST = {}
                    else:
                        return redirect(request.get_full_path())
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def ajax(template_name):
    """
    A view decorator that will swap in an alternative template name for any
    TemplateResponse to an ajax request.

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            if request.is_ajax() and hasattr(response, "template_name"):
                response.template_name = template_name
            return response

        return _wrapped_view

    return decorator



def finder(finder_cls):
    """
    View decorator that takes care of everything needed to render a finder on
    the rendered page.

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            finder = finder_cls(request.auth)
            if request.is_ajax() and request.GET.get("finder"):
                col_name = request.GET["col"]
                return render(
                    request,
                    finder.column_template(col_name),
                    {
                        "finder": {
                            "finder": finder,
                            col_name: finder.objects(
                                col_name, request.GET["id"])
                            },
                        }
                    )
            response = view_func(request, *args, **kwargs)
            try:
                ctx = response.context_data
            except AttributeError:
                return response
            top_col = finder.columns[0]
            finder_ctx = ctx.setdefault("finder", {})
            finder_ctx.update(
                {
                    "finder": finder,
                    top_col.name: finder.objects(top_col.name)
                    }
                )
            return response

        return _wrapped_view

    return decorator


def as_admin(method):
    """
    A decorator for methods of an api.RemoteObject that causes the method to be
    executed with admin permissions, without disturbing the credentials stored
    on the object itself.

    """
    @wraps(method)
    def _wrapped(self, *args, **kwargs):
        auth = self.auth
        self.auth = admin
        ret = method(self, *args, **kwargs)
        self.auth = auth
        return ret
    return _wrapped
