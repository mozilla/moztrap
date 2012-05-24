"""
Ajax view decorators.

"""
from functools import wraps


def ajax(template_name):
    """Swaps in an alternative template name for any ajax TemplateResponse."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            if request.is_ajax() and hasattr(response, "template_name"):
                response.template_name = template_name
            return response

        return _wrapped_view

    return decorator
