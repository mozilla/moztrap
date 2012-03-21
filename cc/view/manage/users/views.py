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
Manage views for users.

"""
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from cc import model

from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ManageFinder

from .filters import UserFilterSet
from . import forms



@never_cache
@login_required
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
                request, "User '{0}' added.".format(
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
            messages.success(request, "Saved '{0}'.".format(u.username))
            return redirect("manage_users")
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
