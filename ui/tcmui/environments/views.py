from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..products.models import Product
from ..users.decorators import login_required

from .forms import EnvironmentSelectionForm



@login_required
def set_environment(request, product_id):
    """
    Given the context of a ``product_id``, allow the user to choose a valid
    environment-group for that product, set that environment-group ID in the
    user's session, and redirect to the list of test cycles for that
    environment (or a "next" URL given in querystring).

    """
    next = request.REQUEST.get("next", "cycles")
    product = Product.get("products/%s" % product_id, auth=request.auth)
    form = EnvironmentSelectionForm(
        request.POST or None, groups=product.environmentgroups)

    if request.method == "POST" and form.is_valid():
        request.session["environment_group_id"] = form.save()
        return redirect(next)

    return TemplateResponse(
        request,
        "test/environment.html",
        {"product": product, "form": form, "next": next}
        )
