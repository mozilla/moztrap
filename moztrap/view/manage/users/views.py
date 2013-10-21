"""
Manage views for users.

"""
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages

from moztrap import model

from moztrap.view.lists import decorators as lists
from moztrap.view.users.decorators import permission_required
from moztrap.view.utils.ajax import ajax

from ..finders import ManageFinder

from .filters import UserFilterSet
from . import forms



@never_cache
@permission_required("core.manage_users")
@lists.actions(
    model.User,
    ["delete", "activate", "deactivate"],
    permission="core.manage_users")
@lists.finder(ManageFinder)
@lists.filter("users", filterset_class=UserFilterSet)
@lists.sort("users")
@ajax("manage/user/list/_users_list.html")
def users_list(request):
    """List users."""
    return TemplateResponse(
        request,
        "manage/user/users.html",
        {
            "users": model.User.objects.all(),
            }
        )



@never_cache
@permission_required("core.manage_users")
def user_add(request):
    """Add a user."""
    if request.method == "POST":
        form = forms.AddUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, u"User '{0}' added.".format(
                    user.username)
                )
            return redirect("manage_users")
    else:
        form = forms.AddUserForm()
    return TemplateResponse(
        request,
        "manage/user/add_user.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("core.manage_users")
def user_edit(request, user_id):
    """Edit a user."""
    user = get_object_or_404(model.User, pk=user_id)
    if request.method == "POST":
        form = forms.EditUserForm(
            request.POST, instance=user)
        if form.is_valid():
            u = form.save()
            messages.success(request, u"Saved '{0}'.".format(u.username))
            pre_page = request.GET.get('from', "manage_users")
            return redirect(pre_page)
    else:
        form = forms.EditUserForm(instance=user)
    return TemplateResponse(
        request,
        "manage/user/edit_user.html",
        {
            "form": form,
            "subject": user,
            }
        )
