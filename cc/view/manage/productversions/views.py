# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Manage views for productversions.

"""
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from cc import model

from cc.view.filters import ProductVersionFilterSet
from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ManageFinder

from . import forms



@login_required
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



@login_required
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



@permission_required("core.manage_products")
def productversion_add(request):
    """Add a product version."""
    if request.method == "POST":
        form = forms.AddProductVersionForm(request.POST, user=request.user)
        if form.is_valid():
            productversion = form.save()
            messages.success(
                request, "Product version '{0}' added.".format(
                    productversion.name)
                )
            return redirect("manage_productversions")
    else:
        form = forms.AddProductVersionForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/productversion/add_productversion.html",
        {
            "form": form
            }
        )



@permission_required("core.manage_products")
def productversion_edit(request, productversion_id):
    """Edit a productversion."""
    productversion = get_object_or_404(
        model.ProductVersion, pk=productversion_id)
    if request.method == "POST":
        form = forms.EditProductVersionForm(
            request.POST, instance=productversion, user=request.user)
        if form.is_valid():
            pv = form.save()
            messages.success(request, "Saved '{0}'.".format(pv.name))
            return redirect("manage_productversions")
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
