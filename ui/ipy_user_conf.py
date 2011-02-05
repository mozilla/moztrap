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
        "from tcmui.core.api import admin, Credentials",
        "from tcmui.core.models import Company, CompanyList",
        "from tcmui.users.models import User, UserList, Role, RoleList, Permission, PermissionList",
        "from tcmui.products.models import Product, ProductList",
        "from tcmui.environments.models import EnvironmentType, EnvironmentTypeList, Environment, EnvironmentList, EnvironmentGroup, EnvironmentGroupList",
        "from tcmui.testexecution.models import TestCycle, TestCycleList, TestRun, TestRunList",
        "from tcmui.testcases.models import TestCase, TestCaseList, TestCaseVersion, TestCaseVersionList",
        ]

    for imp in imports:
        ip.ex(imp)
        print imp

    print "\n"

main()
