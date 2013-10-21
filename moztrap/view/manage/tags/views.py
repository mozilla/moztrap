"""
Manage views for tags.

"""
import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages

from moztrap import model

from moztrap.view.filters import TagFilterSet
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
            "tags": model.Tag.objects.select_related("product", "created_by"),
            }
        )



@never_cache
@login_maybe_required
def tag_details(request, tag_id):
    """Get details snippet for a tag."""
    tag = get_object_or_404(
        model.Tag, pk=tag_id)
    return TemplateResponse(
        request,
        "manage/tag/list/_tag_details.html",
        {
            "tag": tag
        }
    )



@never_cache
@permission_required("tags.manage_tags")
def tag_add(request):
    """Add a tag."""
    if request.method == "POST":
        form = forms.AddTagForm(request.POST, user=request.user)
        tag = form.save_if_valid()
        if tag is not None:
            messages.success(
                request, u"Tag '{0}' added.".format(
                    tag.name)
                )
            return redirect("manage_tags")
    else:
        pf = PinnedFilters(request.COOKIES)
        form = forms.AddTagForm(
            user=request.user,
            initial=pf.fill_form_querystring(request.GET).dict(),
            )
    return TemplateResponse(
        request,
        "manage/tag/add_tag.html",
        {
            "form": form,
            "hide_multiselect": 1,
            }
        )



@never_cache
@permission_required("tags.manage_tags")
def tag_edit(request, tag_id):
    """Edit a tag."""
    tag = get_object_or_404(model.Tag, pk=tag_id)
    if request.method == "POST":
        form = forms.EditTagForm(
            request.POST, instance=tag, user=request.user)
        saved_tag = form.save_if_valid()
        if saved_tag is not None:
            messages.success(request, u"Saved '{0}'.".format(saved_tag.name))
            pre_page = request.GET.get('from', "manage_tags")
            return redirect(pre_page)
    else:
        form = forms.EditTagForm(instance=tag, user=request.user)
    return TemplateResponse(
        request,
        "manage/tag/edit_tag.html",
        {
            "form": form,
            "tag": tag,
            "hide_multiselect": (tag.product is None),
            }
        )



@never_cache
@login_maybe_required
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
        post = tag.name[start + len(text):]
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
