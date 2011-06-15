import logging

from .conf import conf
from .auth import admin
from .models import Company



class StaticCompanyMiddleware(object):
    def __init__(self):
        self.company = Company.get(
            "companies/%s" % conf.TCM_COMPANY_ID,
            auth=admin
            )
        self.company.deliver()


    def process_request(self, request):
        request.company = self.company



log = logging.getLogger("tcmui.core.middleware.RequestLogMiddleware")



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
