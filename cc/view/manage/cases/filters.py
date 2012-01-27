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
Filtering for cases.

"""
from django.contrib.auth.models import User

from .... import model

from ...lists import filters



class CaseVersionFilterSet(filters.FilterSet):
    """FilterSet for CaseVersions; filters on latest by default."""
    filters = [
        filters.ChoicesFilter("status", choices=model.CaseVersion.STATUS),
        filters.KeywordExactFilter("id", lookup="case__id", coerce=int),
        filters.KeywordFilter("name"),
        filters.ModelFilter(
            "tag", lookup="tags", queryset=model.Tag.objects.all()),
        filters.ModelFilter(
            "product",
            lookup="case__product",
            queryset=model.Product.objects.all()),
        filters.ModelFilter(
            "product version",
            lookup="productversion",
            key="productversion",
            queryset=model.ProductVersion.objects.all()),
        filters.KeywordFilter("instruction", lookup="steps__instruction"),
        filters.KeywordFilter(
            "expected result",
            lookup="steps__expected",
            key="expected"),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=User.objects.all()),
        filters.ModelFilter(
            "environment element",
            lookup="environments__elements",
            key="envelement",
            queryset=model.Element.objects.all()),
        filters.ModelFilter(
            "suite", lookup="case__suites", queryset=model.Suite.objects.all()),
        ]


    def filter(self, queryset):
        """Add a filter on latest=True if not filtered on productversion."""
        queryset = super(CaseVersionFilterSet, self).filter(queryset)
        pv = [bf for bf in self if bf.key == "productversion"][0]
        if not pv.values:
            queryset = queryset.filter(latest=True)
        return queryset
