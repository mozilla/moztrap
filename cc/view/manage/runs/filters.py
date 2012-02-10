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
Filtering for runs.

"""
from cc import model
from cc.view.lists import filters



class RunFilterSet(filters.FilterSet):
    """FilterSet for runs."""
    filters = [
        filters.ChoicesFilter("status", choices=model.Run.STATUS),
        filters.ModelFilter(
            "product",
            lookup="productversion__product",
            queryset=model.Product.objects.all()),
        filters.ModelFilter(
            "productversion", queryset=model.ProductVersion.objects.all()),
        filters.KeywordFilter("name"),
        filters.KeywordFilter("description"),
        filters.ModelFilter(
            "suite",
            lookup="suites",
            queryset=model.Suite.objects.all()),
        filters.KeywordExactFilter(
            "case id", lookup="suites__cases__id", key="case", coerce=int),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=model.User.objects.all()),
        filters.ModelFilter(
            "environment element",
            lookup="environments__elements",
            key="envelement",
            queryset=model.Element.objects.all()),
        ]
