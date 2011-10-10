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
from ..builder import ListBuilder
from ..responses import make_locator, make_boolean



testcycles = ListBuilder(
    "testcycle",
    "testcycles",
    "Testcycle",
    {
        "communityAccessAllowed": False,
        "communityAuthoringAllowed": False,
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "description": "",
        "name": "Default Test Cycle",
        "productId": 1,
        "productLocator": make_locator(
            id=1, url="products/1", name="The Product"),
        "startDate": "2011-01-01T00:00:00Z",
        "testCycleStatusId": 1,
        }
    )



testruns = ListBuilder(
    "testrun",
    "testruns",
    "Testrun",
    {
        "autoAssignToTeam": True,
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "name": "Default Test Run",
        "productId": 1,
        "productLocator": make_locator(
            id=1, url="products/1", name="The Product"),
        "selfAssignAllowed": True,
        "selfAssignLimit": 0,
        "selfAssignPerEnvironment": False,
        "startDate": "2011-01-01T00:00:00Z",
        "testCycleId": 1,
        "testCycleLocator": make_locator(
            id=1, url="testcycles/1", name="The Test Cycle"),
        "testRunStatusId": 1,
        "useLatestVersions": False,
        })



testrunitcs = ListBuilder(
    "includedtestcase",
    "includedtestcases",
    "Includedtestcase",
    {
        "blocking": False,
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "priorityId": 0,
        "productId": 1,
        "productLocator": make_locator(
            id=1, url="products/1", name="The Company"),
        "runOrder": 0,
        "testCaseId": 1,
        "testCaseLocator": make_locator(
            id=1, url="testcases/1", name="The Test Case"),
        "testCaseVersionId": 1,
        "testCaseVersionLocator":
            make_locator(id=1, url="testcases/versions/1"),
        "testCycleId": 1,
        "testCycleLocator": make_locator(
            id=1, url="testcycles/1", name="The Test Cycle"),
        "testRunId": 1,
        "testRunLocator": make_locator(
            id=1, url="testruns/1", name="The Test Run"),
        "testSuiteId": make_boolean(None),
        "testSuiteLocator": make_boolean(None),
        })



testresults = ListBuilder(
    "testresult",
    "testresults",
    "Testresult",
    {
    "actualResult": make_boolean(None),
    "actualTimeInMin": make_boolean(None),
    "approvalStatusId": 1,
    "approvedBy": make_boolean(None),
    "approvedByLocator": make_boolean(None),
    "comment": make_boolean(None),
    "companyId": 1,
    "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
    "failedStepNumber": make_boolean(None),
    "productId": 1,
    "productLocator": make_locator(
            id=1, url="products/1", name="The Product"),
    "testCaseId": 1,
    "testCaseLocator": make_locator(
            id=1, url="testcases/1", name="The Test Case"),
    "testCaseVersionId": 1,
    "testCaseVersionLocator": make_locator(
            id=1, url="testcases/versions/1", name="The Test Case Version"),
    "testCycleId": 1,
    "testCycleLocator": make_locator(
            id=1, url="testcycles/1", name="The Test Cycle"),
    "testRunId": 1,
    "testRunLocator": make_locator(
            id=1, url="testruns/1", name="The Test Run"),
    "testRunResultStatusId": 1,
    "testSuiteId": make_boolean(None),
    "testSuiteLocator": make_boolean(None),
    "testerId": 1,
    "testerLocator": "users/1",
    })



assignments = ListBuilder(
    "testcaseassignment",
    "testcaseassignments",
    "Testcaseassignment",
    {
    "companyId": 1,
    "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
    "productId": 1,
    "productLocator": make_locator(
            id=1, url="products/1", name="The Product"),
    "testCaseId": 1,
    "testCaseLocator": make_locator(
            id=1, url="testcases/1", name="The Test Case"),
    "testCaseVersionId": 1,
    "testCaseVersionLocator": make_locator(
            id=1, url="testcases/versions/1", name="The Test Case Version"),
    "testCycleId": 1,
    "testCycleLocator": make_locator(
            id=1, url="testcycles/1", name="The Test Cycle"),
    "testRunId": 1,
    "testRunLocator": make_locator(
            id=1, url="testruns/1", name="The Test Run"),
    "testSuiteId": make_boolean(None),
    "testSuiteLocator": make_boolean(None),
    "testerId": 1,
    "testerLocator": make_locator(
            id=1, url="users/1", name="The Tester"),
        }
    )
