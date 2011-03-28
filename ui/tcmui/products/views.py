from django.template.response import TemplateResponse

from ..environments.models import EnvironmentGroupList
from ..users.decorators import login_redirect

from .models import ProductList


@login_redirect
def product_list(request):
    return TemplateResponse(
        request,
        "test/products.html",
        {"products":
             ProductList.ours(auth=request.auth),
         "environmentgroups": EnvironmentGroupList.ours(auth=request.auth)
         }
    )
