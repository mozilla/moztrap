# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
Decorator for ajaxily editing/adding environment categories and elements.

@@@ This needs a rewrite, but the UI it supports needs a rethink first.

"""
from functools import wraps
import json

from django.contrib import messages
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string

from cc import model
from cc.view.lists.actions import get_action



ACTION_TYPES = {
    "category": (
        model.Category,
        "manage/environment/add_profile/_category_list_item.html",
        ),
    "element": (
        model.Element,
        "manage/environment/add_profile/_element_list_item.html",
        ),
    }



def category_element_ajax_add_edit(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.is_ajax() and request.method == "POST":
            data = {}

            action_data = get_action(request.POST)
            if action_data:
                action, obj_spec = action_data
                if action in ["delete"]:
                    obj_type, obj_id = obj_spec.split("-")
                    model_class, template_name = ACTION_TYPES[obj_type]
                    try:
                        obj = model_class.objects.get(pk=obj_id)
                    except model_class.DoesNotExist:
                        data["no_replace"] = True
                        success = False
                    else:
                        getattr(obj, action)(user=request.user)
                        success = True

                    if action == "delete":
                        if success:
                            data["html"] = ""
                        else:
                            data["no_replace"] = True
                    else:
                        data["html"] = render_to_string(
                            template_name,
                            {obj_type: obj},
                            RequestContext(request))
            elif "new-category-name" in request.POST:
                template_name = ACTION_TYPES["category"][1]
                new_category_name = request.POST.get("new-category-name")
                if not new_category_name:
                    messages.error(
                        request, "Please enter a category name.")
                    data["no_replace"] = True
                else:
                    cat = model.Category.objects.create(
                        name=new_category_name
                        )
                    data["html"] = render_to_string(
                        template_name,
                        {"category": cat},
                        RequestContext(request)
                        )
            elif "new-element-name" in request.POST:
                template_name = ACTION_TYPES["element"][1]
                preview_template_name = (
                    "manage/environment/add_profile/"
                    "_element_preview_list_item.html")
                new_element_name = request.POST.get("new-element-name")

                if not new_element_name:
                    messages.error(
                        request, "Please enter an element name.")
                    data["no_replace"] = True
                else:
                    if "element-id" in request.POST:
                        e = model.Element.objects.get(
                            pk=request.POST.get("element-id"),
                            )
                        e.name = new_element_name
                        e.save()
                    else:
                        e = model.Element.objects.create(
                            name=new_element_name,
                            category=request.POST.get("category-id")
                            )

                    data["elem"] = render_to_string(
                        template_name,
                        {"element": e},
                        RequestContext(request))

                    data["preview"] = render_to_string(
                        preview_template_name,
                        {"element": e},
                        RequestContext(request))

            return HttpResponse(
                json.dumps(data), content_type="application/json")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
