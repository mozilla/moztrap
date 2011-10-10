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
from ..static import filters as status_filters
from ..testcases.filters import TestSuiteFieldFilter
from ..testexecution.filters import TestCycleFieldFilter, TestRunFieldFilter



class NonDraftTestCycleStatusFilter(status_filters.TestCycleStatusFilter):
    options = [
        (k, v) for k, v
        in status_filters.TestCycleStatusFilter.options
        if v != "draft"]



class NonDraftTestRunStatusFilter(status_filters.TestRunStatusFilter):
    options = [
        (k, v) for k, v
        in status_filters.TestRunStatusFilter.options
        if v != "draft"]



class NonDraftTestCaseStatusFilter(status_filters.TestCaseStatusFilter):
    options = [
        (k, v) for k, v
        in status_filters.TestCaseStatusFilter.options
        if v != "draft"]



class NonDraftTestCycleFieldFilter(TestCycleFieldFilter):
    target_filters = {"status": [2, 3]}



class NonDraftTestRunFieldFilter(TestRunFieldFilter):
    target_filters = {"status": [2, 3]}



class NonDraftTestSuiteFieldFilter(TestSuiteFieldFilter):
    target_filters = {"status": [2, 3]}
