# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
from ..core.finder import Finder, Column
from ..products.models import ProductList
from ..testcases.models import TestSuiteList
from ..testexecution.models import TestCycleList, TestRunList



class ManageFinder(Finder):
    template_base = "manage/finder"

    columns = [
        Column("products", "_products.html", ProductList, "product",
               goto="manage_testcycles"),
        Column("cycles", "_cycles.html", TestCycleList, "testCycle",
               goto="manage_testruns"),
        Column("runs", "_runs.html", TestRunList, "run",
               goto="manage_testsuites"),
        Column("suites", "_suites.html", TestSuiteList, "suite",
               goto="manage_testcases"),
        ]
