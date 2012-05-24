from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse



class AjaxTracebackMiddleware(object):
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed


    def process_exception(self, request, *args, **kwargs):
        if request.is_ajax():
            import traceback
            return HttpResponse(traceback.format_exc().replace("\n", "<br>\n"))
