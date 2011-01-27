from django.template.response import TemplateResponse

from ..core import conf
from ..users.decorators import login_required

from .models import ProductList


@login_required
def product_list(request):
    return TemplateResponse(
        request,
        "test/products.html",
        {"products":
             ProductList.get(auth=request.user.auth).filter(
                companyId=conf.TCM_COMPANY_ID)}
    )
