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
"""
Makes IPython import all of your projects models when shell is started.

1. Save as ipy_user_conf.py in project root
2. ./manage.py shell
3. profit

"""

import IPython.ipapi
ip = IPython.ipapi.get()


def main():
    print "\nImported:\n\n"

    imports = [
        "import datetime",
        "from ccui.attachments.models import Attachment, AttachmentList",
        "from ccui.core.auth import admin, Credentials",
        "from ccui.core.models import Company, CompanyList",
        "from ccui.users.models import User, UserList, Role, RoleList, Permission, PermissionList",
        "from ccui.products.models import Product, ProductList",
        "from ccui.relatedbugs.models import ExternalBug, ExternalBugList",
        "from ccui.environments.models import EnvironmentType, EnvironmentTypeList, Environment, EnvironmentList, EnvironmentGroup, ExplodedEnvironmentGroup, EnvironmentGroupList, ExplodedEnvironmentGroupList",
        "from ccui.static import status",
        "from ccui.tags.models import Tag, TagList",
        "from ccui.testexecution.models import TestCycle, TestCycleList, TestRun, TestRunList, TestRunIncludedTestCase, TestRunIncludedTestCaseList, TestCaseAssignment, TestCaseAssignmentList, TestResult, TestResultList",
        "from ccui.testcases.models import TestCase, TestCaseList, TestCaseVersion, TestCaseVersionList, TestCaseStep, TestCaseStepList, TestSuite, TestSuiteList",
        ]

    for imp in imports:
        ip.ex(imp)
        print imp

    print "\n"

main()
