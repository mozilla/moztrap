"""
Decorator for ajaxily editing/adding environment categories and elements.

@@@ This needs a rewrite, but the UI it supports needs a rethink first.

"""
from functools import wraps
import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string

from django.contrib import messages

from moztrap import model



ACTION_TYPES = {
    "category": (
        model.Category,
        "manage/environment/element_select/_category_list_item.html",
        ),
    "element": (
        model.Element,
        "manage/environment/element_select/_element_list_item.html",
        ),
    }



def category_element_ajax_add_edit(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.is_ajax() and request.method == "POST":
            data = {}

            if "action-delete" in request.POST:
                try:
                    obj_type, obj_id = request.POST["action-delete"].split("-")
                    model_class, template_name = ACTION_TYPES[obj_type]
                    obj = model_class.objects.get(pk=obj_id)
                except (KeyError, ValueError, ObjectDoesNotExist):
                    data["no_replace"] = True
                else:
                    obj.delete(user=request.user)
                    data["html"] = ""
            elif "new-category-name" in request.POST:
                template_name = ACTION_TYPES["category"][1]
                new_category_name = request.POST.get("new-category-name")
                if not new_category_name:
                    messages.error(
                        request, "Please enter a category name.")
                    data["no_replace"] = True
                else:
                    if "category-id" in request.POST:
                        cat = model.Category.objects.get(
                            pk=request.POST.get("category-id")
                            )
                        cat.name = new_category_name
                        cat.save()
                    else:
                        cat = model.Category.objects.create(
                            name=new_category_name
                            )
                    # @@@ this ought to be only elements that were included in
                    # the original widget queryset, but we don't have access to
                    # that here. soon this whole editing-on-the-form thing will
                    # go away anyway.
                    cat.choice_elements = cat.elements.order_by("name")
                    data["html"] = render_to_string(
                        template_name,
                        {
                            "category": cat,
                            "selected_element_ids": set(
                                map(int, request.POST.getlist("elements"))),
                            "name": "elements"  # @@@ duplicated form field name
                            },
                        RequestContext(request)
                        )
            elif "new-element-name" in request.POST:
                template_name = ACTION_TYPES["element"][1]
                preview_template_name = (
                    "manage/environment/element_select/"
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
                            category_id=request.POST.get("category-id")
                            )

                    data["elem"] = render_to_string(
                        template_name,
                        {
                            "element": e,
                            "name": "elements"  # @@@ duplicated form field name
                            },
                        RequestContext(request))

                    data["preview"] = render_to_string(
                        preview_template_name,
                        {"element": e},
                        RequestContext(request))

            return HttpResponse(
                json.dumps(data), content_type="application/json")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
