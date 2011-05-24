from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from . import pagination, filters, errors, sort as sort_util
from .auth import admin



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
            ctx = response.context_data
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
            ctx = response.context_data
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
            ctx = response.context_data
            pagesize, pagenum = pagination.from_request(request)
            ctx[ctx_name] = ctx[ctx_name].paginate(pagesize, pagenum)
            # the lambda here makes Pager fetch the total result count
            # lazily; another decorator might modify the result set yet.
            ctx["pager"] = pagination.Pager(
                lambda: ctx[ctx_name].totalResults, pagesize, pagenum)
            return response

        return _wrapped_view

    return decorator


def actions(list_model, allowed_actions, fall_through=False):
    """
    View decorator that handles any POST keys named "action-method", where
    "method" must be in ``allowed_actions``. The value of the key should be an
    ID of ``list_model``, and "method" will be called on it, with any errors
    handled.

    By default, any "POST" request will be redirected back to the same URL. If
    ``fall_through`` is set to True, the redirect will only occur if an action
    was found in the POST data (allowing this decorator to be used with views
    that also do normal form handling.)

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method == "POST":
                action_taken = False
                actions = [(k, v) for k, v in request.POST.iteritems()
                           if k.startswith("action-")]
                if actions:
                    action, obj_id = actions[0]
                    action = action[len("action-"):]
                    if action in allowed_actions:
                        obj = list_model.get_by_id(obj_id, auth=request.auth)
                        try:
                            getattr(obj, action)()
                        except obj.Conflict, e:
                            messages.error(
                                request, errors.error_message(obj, e))
                        action_taken = True
                if action_taken or not fall_through:
                    return redirect(request.get_full_path())
            return view_func(request, *args, **kwargs)

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
