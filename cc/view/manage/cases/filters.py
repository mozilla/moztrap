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
from ....model.core.models import Product, ProductVersion
from ....model.library.models import CaseVersion

from ...lists import filters



class CaseVersionFilterSet(filters.FilterSet):
    """FilterSet for CaseVersions; filters on latest by default."""
    filters = [
        filters.ChoicesFilter("status", choices=CaseVersion.STATUS),
        filters.RelatedFieldFilter(
            "product", lookup="case__product", queryset=Product.objects.all()),
        filters.RelatedFieldFilter(
            "product version",
            lookup="productversion",
            key="productversion",
            queryset=ProductVersion.objects.all()),
        ]


    def filter(self, queryset):
        """Add a filter on latest=True if not filtered on productversion."""
        queryset = super(CaseVersionFilterSet, self).filter(queryset)
        if "productversion" not in self.data:
            queryset = queryset.filter(latest=True)
        return queryset
