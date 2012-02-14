# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
Finder for results pages.

"""
from django.core.urlresolvers import reverse

from ... import model
from ..lists import finder



class CaseColumn(finder.Column):
    """Finder column for case results; goto is to case-results-list."""
    def goto_url(self, obj):
        """Given an object, return its "Goto" url, or None."""
        if self.goto:
            return reverse(self.goto, kwargs={"rcv_id": obj.id})

        return None



class ResultsFinder(finder.Finder):
    template_base = "results/finder"

    columns = [
        finder.Column(
            "products",
            "_products.html",
            model.Product.objects.order_by("name"),
            ),
        finder.Column(
            "productversions",
            "_productversions.html",
            model.ProductVersion.objects.all(),
            "results_runs",
            ),
        finder.Column(
            "runs",
            "_runs.html",
            model.Run.objects.order_by("start"),
            "results_runcaseversions",
            ),
        CaseColumn(
            "cases",
            "_cases.html",
            model.RunCaseVersion.objects.order_by("caseversion__name"),
            "results_results",
            ),
        ]
