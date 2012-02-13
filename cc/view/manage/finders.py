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
Finder for management pages.

"""
from ... import model
from ..lists import finder



class ManageFinder(finder.Finder):
    template_base = "manage/finder"

    columns = [
        finder.Column(
            "products",
            "_products.html",
            model.Product.objects.order_by("name"),
            "manage_productversions",
            ),
        finder.Column(
            "productversions",
            "_productversions.html",
            model.ProductVersion.objects.all(),
            "manage_runs",
            ),
        finder.Column(
            "runs",
            "_runs.html",
            model.Run.objects.order_by("start"),
            "manage_suites",
            ),
        finder.Column(
            "suites",
            "_suites.html",
            model.Suite.objects.order_by("name"),
            "manage_cases",
            ),
        ]
