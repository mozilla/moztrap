from . import conf
from .api import admin
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



class SecurityMiddleware(object):
    def __init__(self):
        self.sts_seconds = conf.HTTPS_STS_SECONDS


    def process_response(self, request, response):
        if not 'x-frame-options' in response:
            response["x-frame-options"] = "DENY"
        if self.sts_seconds and not 'strict-transport-security' in response:
            response["strict-transport-security"] = ("max-age=%s"
                                                     % self.sts_seconds)
        return response
