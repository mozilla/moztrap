"""
Manage views for products.

"""
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages

from cc import model

from cc.view.filters import ProductFilterSet
from cc.view.lists import decorators as lists
from cc.view.users.decorators import permission_required
from cc.view.utils.ajax import ajax
from cc.view.utils.auth import login_maybe_required

from ..finders import ManageFinder

from . import forms



@never_cache
@login_maybe_required
@lists.actions(
    model.Product,
    ["delete", "clone"],
    permission="core.manage_products")
@lists.finder(ManageFinder)
@lists.filter("products", filterset_class=ProductFilterSet)
@lists.sort("products")
@ajax("manage/product/list/_products_list.html")
def products_list(request):
    """List products."""
    return TemplateResponse(
        request,
        "manage/product/products.html",
        {
            "products": model.Product.objects.all(),
            }
        )



@never_cache
@login_maybe_required
def product_details(request, product_id):
    """Get details snippet for a product."""
    product = get_object_or_404(model.Product, pk=product_id)
    return TemplateResponse(
        request,
        "manage/product/list/_product_details.html",
        {
            "product": product
            }
        )



@never_cache
@permission_required("core.manage_products")
def product_add(request):
    """Add a product."""
    if request.method == "POST":
        form = forms.AddProductForm(request.POST, user=request.user)
        product = form.save_if_valid()
        if product is not None:
            messages.success(
                request, "Product '{0}' added.".format(
                    product.name)
                )
            return redirect("manage_products")
    else:
        form = forms.AddProductForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/product/add_product.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("core.manage_products")
def product_edit(request, product_id):
    """Edit a product."""
    product = get_object_or_404(model.Product, pk=product_id)
    if request.method == "POST":
        form = forms.EditProductForm(
            request.POST, instance=product, user=request.user)
        saved_product = form.save_if_valid()
        if saved_product is not None:
            messages.success(request, "Saved '{0}'.".format(saved_product.name))
            return redirect("manage_products")
    else:
        form = forms.EditProductForm(instance=product, user=request.user)
    return TemplateResponse(
        request,
        "manage/product/edit_product.html",
        {
            "form": form,
            "product": product,
            }
        )
