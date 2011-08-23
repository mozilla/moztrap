import logging

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse



log = logging.getLogger("ccui.core.middleware.RequestLogMiddleware")



class RequestLogMiddleware(object):
    def process_request(self, request):
        log.debug(
            "%(method)s %(url)s",
            {
                "method": request.method,
                "url": request.get_full_path(),
                "request": request
                }
            )



class AjaxTracebackMiddleware(object):
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed


    def process_exception(self, request, *args, **kwargs):
        if request.is_ajax():
            import traceback
            return HttpResponse(traceback.format_exc().replace("\n", "<br>\n"))
