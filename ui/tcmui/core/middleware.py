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
