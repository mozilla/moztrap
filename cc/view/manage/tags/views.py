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
Manage views for tags.

"""
import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from cc import model

from cc.view.filters import TagFilterSet
from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ManageFinder

from . import forms



@login_required
@lists.actions(
    model.Tag,
    ["delete", "clone"],
    permission="tags.manage_tags")
@lists.finder(ManageFinder)
@lists.filter("tags", filterset_class=TagFilterSet)
@lists.sort("tags")
@ajax("manage/tag/list/_tags_list.html")
def tags_list(request):
    """List tags."""
    return TemplateResponse(
        request,
        "manage/tag/tags.html",
        {
            "tags": model.Tag.objects.all(),
            }
        )



@permission_required("tags.manage_tags")
def tag_add(request):
    """Add a tag."""
    if request.method == "POST":
        form = forms.AddTagForm(request.POST, user=request.user)
        if form.is_valid():
            tag = form.save()
            messages.success(
                request, "Tag '{0}' added.".format(
                    tag.name)
                )
            return redirect("manage_tags")
    else:
        form = forms.AddTagForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/tag/add_tag.html",
        {
            "form": form
            }
        )



@permission_required("tags.manage_tags")
def tag_edit(request, tag_id):
    """Edit a tag."""
    tag = get_object_or_404(model.Tag, pk=tag_id)
    if request.method == "POST":
        form = forms.EditTagForm(
            request.POST, instance=tag, user=request.user)
        if form.is_valid():
            tag = form.save()
            messages.success(request, "Saved '{0}'.".format(tag.name))
            return redirect("manage_tags")
    else:
        form = forms.EditTagForm(instance=tag, user=request.user)
    return TemplateResponse(
        request,
        "manage/tag/edit_tag.html",
        {
            "form": form,
            "tag": tag,
            }
        )



@login_required
def tag_autocomplete(request):
    """Return autocomplete list of existing tags in JSON format."""
    text = request.GET.get("text")
    product_id = request.GET.get("product-id")
    if text is not None:
        tags = model.Tag.objects.filter(name__icontains=text)
        if product_id is not None:
            tags = tags.filter(Q(product=product_id) | Q(product=None))
    else:
        tags = []
    suggestions = []
    for tag in tags:
        # can't just use split due to case; we match "text" insensitively, but
        # want pre and post to be case-accurate
        start = tag.name.lower().index(text.lower())
        pre = tag.name[:start]
        post = tag.name[start+len(text):]
        suggestions.append({
                "preText": pre,
                "typedText": text,
                "postText": post,
                "id": tag.id,
                "product-id": tag.product.id if tag.product else None,
                "name": tag.name,
                "type": "tag",
                })
    return HttpResponse(
        json.dumps(
            {
                "suggestions": suggestions
                }
            ),
        content_type="application/json",
        )
