"""
Manage views for productversions.

"""
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages

from moztrap import model

from moztrap.view.filters import ProductVersionFilterSet
from moztrap.view.lists import decorators as lists
from moztrap.view.lists.filters import PinnedFilters
from moztrap.view.users.decorators import permission_required
from moztrap.view.utils.ajax import ajax
from moztrap.view.utils.auth import login_maybe_required

from ..finders import ManageFinder

from . import forms



@never_cache
@login_maybe_required
@lists.actions(
    model.ProductVersion,
    ["delete", "clone"],
    permission="core.manage_products")
@lists.finder(ManageFinder)
@lists.filter("productversions", filterset_class=ProductVersionFilterSet)
@lists.sort("productversions")
@ajax("manage/productversion/list/_productversions_list.html")
def productversions_list(request):
    """List productversions."""
    return TemplateResponse(
        request,
        "manage/productversion/productversions.html",
        {
            "productversions": model.ProductVersion.objects.select_related(
                "product"),
            }
        )



@never_cache
@login_maybe_required
def productversion_details(request, productversion_id):
    """Get details snippet for a productversion."""
    productversion = get_object_or_404(
        model.ProductVersion, pk=productversion_id)
    return TemplateResponse(
        request,
        "manage/productversion/list/_productversion_details.html",
        {
            "productversion": productversion
            }
        )



@never_cache
@permission_required("core.manage_products")
def productversion_add(request):
    """Add a product version."""
    if request.method == "POST":
        form = forms.AddProductVersionForm(request.POST, user=request.user)
        productversion = form.save_if_valid()
        if productversion is not None:
            messages.success(
                request, u"Product version '{0}' added.".format(
                    productversion.name)
                )
            return redirect("manage_productversions")
    else:
        pf = PinnedFilters(request.COOKIES)
        form = forms.AddProductVersionForm(
            user=request.user,
            initial=pf.fill_form_querystring(request.GET).dict(),
            )
    return TemplateResponse(
        request,
        "manage/productversion/add_productversion.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("core.manage_products")
def productversion_edit(request, productversion_id):
    """Edit a productversion."""
    productversion = get_object_or_404(
        model.ProductVersion, pk=productversion_id)
    if request.method == "POST":
        form = forms.EditProductVersionForm(
            request.POST, instance=productversion, user=request.user)
        pv = form.save_if_valid()
        if pv is not None:
            messages.success(request, u"Saved '{0}'.".format(pv.name))
            pre_page = request.GET.get('from', "manage_productversions")
            return redirect(pre_page)
    else:
        form = forms.EditProductVersionForm(
            instance=productversion, user=request.user)
    return TemplateResponse(
        request,
        "manage/productversion/edit_productversion.html",
        {
            "form": form,
            "productversion": productversion,
            }
        )
