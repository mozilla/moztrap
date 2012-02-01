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
Actions-handling for manage list pages.

"""
from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect



def actions(model, allowed_actions, permission=None, fall_through=False):
    """
    View decorator for handling single-model actions on manage list pages.

    Handles any POST keys named "action-method", where "method" must be in
    ``allowed_actions``. The value of the key should be an ID of a ``model``,
    and "method" will be called on it, with any errors handled.

    By default, any "POST" request will be redirected back to the same URL
    (unless it's an AJAX request, in which case it sets the request method to
    GET and clears POST data, which has a similar effect without actually doing
    a redirect). If ``fall_through`` is set to True, the redirect/method-switch
    will only occur if an action was found in the POST data (allowing this
    decorator to be used with views that also do normal non-actions form
    handling.)

    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method == "POST":
                action_taken = False
                action_data = get_action(request.POST)
                if action_data:
                    action, obj_id = action_data
                    if action in allowed_actions:
                        if permission and not request.user.has_perm(permission):
                            return HttpResponseForbidden(
                                "You do not have permission for this action.")
                        try:
                            obj = model._base_manager.get(pk=obj_id)
                        except model.DoesNotExist:
                            pass
                        else:
                            getattr(obj, action)(user=request.user)
                            action_taken = True
                if action_taken or not fall_through:
                    if request.is_ajax():
                        request.method = "GET"
                        request.POST = {}
                    else:
                        return redirect(request.get_full_path())
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator



def get_action(post_data):
    """
    Given a request.POST including e.g. {"action-delete": "3"}, return
    ("delete", "3"). Doesn't care about the value, just looks for POST keys
    beginning with "action-". Returns None if no action found.

    If multiple actions are found, returns only the first.

    """
    actions = [
        (k[len("action-"):], v) for k, v in post_data.iteritems()
        if k.startswith("action-")
        ]
    if actions:
        return actions[0]
    return None
