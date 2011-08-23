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
        "from ccui.core.auth import admin, Credentials",
        "from ccui.core.models import Company, CompanyList",
        "from ccui.users.models import User, UserList, Role, RoleList, Permission, PermissionList",
        "from ccui.products.models import Product, ProductList",
        "from ccui.environments.models import EnvironmentType, EnvironmentTypeList, Environment, EnvironmentList, EnvironmentGroup, EnvironmentGroupList",
        "from ccui.testexecution.models import TestCycle, TestCycleList, TestRun, TestRunList, TestRunIncludedTestCase, TestRunIncludedTestCaseList, TestCaseAssignment, TestCaseAssignmentList, TestResult, TestResultList",
        "from ccui.testcases.models import Tag, TagList, TestCase, TestCaseList, TestCaseVersion, TestCaseVersionList, TestCaseStep, TestCaseStepList, TestSuite, TestSuiteList",
        ]

    for imp in imports:
        ip.ex(imp)
        print imp

    print "\n"

main()
