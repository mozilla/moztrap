from django.template.response import TemplateResponse

from ..core.conf import conf
from ..environments.models import EnvironmentGroupList
from ..users.decorators import login_redirect

from .models import ProductList


@login_redirect
def product_list(request):
    return TemplateResponse(
        request,
        "test/products.html",
        {"products":
             ProductList.get(auth=request.auth).filter(
                companyId=conf.TCM_COMPANY_ID),
         "environmentgroups": EnvironmentGroupList.ours(auth=request.auth)
         }
    )
