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
Filtering for suites.

"""
from cc import model
from cc.view.lists import filters



class SuiteFilterSet(filters.FilterSet):
    """FilterSet for suites."""
    filters = [
        filters.ChoicesFilter("status", choices=model.Suite.STATUS),
        filters.ModelFilter("product", queryset=model.Product.objects.all()),
        filters.ModelFilter(
            "run",
            lookup="runs",
            queryset=model.Run.objects.all()
            ),
        filters.KeywordFilter("name"),
        filters.KeywordFilter("description"),
        filters.KeywordExactFilter(
            "case id", lookup="cases__id", key="case", coerce=int),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=model.User.objects.all()),
        ]
