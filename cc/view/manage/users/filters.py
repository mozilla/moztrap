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
Filtering for users.

"""
from cc import model
from cc.view.lists import filters



class UserFilterSet(filters.FilterSet):
    """FilterSet for Users."""
    filters = [
        filters.ChoicesFilter(
            "active",
            lookup="is_active",
            choices=[(1, "active"), (0, "disabled")],
            coerce=int,
            ),
        filters.KeywordFilter("username"),
        filters.KeywordFilter("email"),
        filters.ModelFilter(
            "role", lookup="groups", queryset=model.Role.objects.all())
        ]
