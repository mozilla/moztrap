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
Manage views for environments.

"""
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from cc import model

from cc.view.filters import ProfileFilterSet
from cc.view.lists import decorators as lists
from cc.view.utils.ajax import ajax

from ..finders import ManageFinder

from . import forms



@login_required
@lists.actions(
    model.Profile,
    ["delete", "clone"],
    permission="environments.manage_environments")
@lists.finder(ManageFinder)
@lists.filter("profiles", filterset_class=ProfileFilterSet)
@lists.sort("profiles")
@ajax("manage/environment/profile_list/_profiles_list.html")
def profiles_list(request):
    """List profiles."""
    return TemplateResponse(
        request,
        "manage/environment/profiles.html",
        {
            "profiles": model.Profile.objects.all(),
            }
        )



@login_required
def profile_details(request, profile_id):
    """Get details snippet for a profile."""
    profile = get_object_or_404(model.Profile, pk=profile_id)
    return TemplateResponse(
        request,
        "manage/environment/profile_list/_profile_details.html",
        {
            "profile": profile
            }
        )



@permission_required("environments.manage_environments")
def profile_add(request):
    """Add an environment profile."""
    if request.method == "POST":
        form = forms.AddProfileForm(request.POST, user=request.user)
        if form.is_valid():
            profile = form.save()
            messages.success(
                request, "Profile '{0}' added.".format(
                    profile.name)
                )
            return redirect("manage_profiles")
    else:
        form = forms.AddProfileForm(user=request.user)
    return TemplateResponse(
        request,
        "manage/environment/add_profile.html",
        {
            "form": form
            }
        )
