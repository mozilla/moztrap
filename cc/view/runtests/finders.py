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
Finder for running tests.

"""
from django.core.urlresolvers import reverse

from ... import model
from ..lists import finder



class RunTestsFinder(finder.Finder):
    template_base = "runtests/finder"

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
            ),
        finder.Column(
            "runs",
            "_runs.html",
            model.Run.objects.filter(status=model.Run.STATUS.active),
            ),
        ]


    def child_query_url(self, obj):
        if isinstance(obj, model.Run):
            return reverse("runtests_environment", kwargs={"run_id": obj.id})
        return super(RunTestsFinder, self).child_query_url(obj)
