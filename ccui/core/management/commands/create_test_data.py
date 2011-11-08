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
import datetime

from django.core.management.base import BaseCommand, CommandError

from ...auth import admin, Credentials
from ...conf import conf
from ...models import Company
from ....environments.models import (
    EnvironmentType, EnvironmentTypeList, Environment, EnvironmentList
    )
from ....products.models import Product, ProductList
from ....testexecution.models import (
    TestCycle, TestCycleList, TestRun, TestRunList
    )
from ....testcases.models import (
    TestSuite, TestSuiteList, TestCaseVersion, TestCaseList, TestCaseStep)
from ....users.models import User, UserList



ENVIRONMENTS = {
    "types": {
        "Browser": [
            "Chrome",
            "Firefox 3",
            "Firefox 4",
            "IE 7",
            "IE 8",
            ],
        "Operating System": [
            "Linux",
            "OS X",
            "Windows XP",
            "Windows 7",
            ],
        "Language": [
            "English",
            "German",
            "Spanish",
            "French",
            ],
        },
    "grouptypes": {
        "Browser Testing Environments": [
            "Operating System",
            "Language",
            ],
        "Website Testing Environments": [
            "Browser",
            "Operating System",
            "Language",
            ],
        },
    }



PRODUCTS = {
    "Firefox": {
        "description": "The browser.",
        "environments": "Browser Testing Environments",
        },
    "Fennec": {
        "description": "The mobile browser.",
        "environments": "Browser Testing Environments",
        },
    "TCM": {
        "description": "The test case manager.",
        "environments": "Website Testing Environments",
        "testers": ["tester", "tester2"],
        "cycles": {
            "Test Cycle 1": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 1",
                "testers": ["tester", "tester2"],
                "testruns": {
                    "Test Run 1A": {
                        "startDate": datetime.date.today(),
                        "selfAssignAllowed": True,
                        "selfAssignLimit": 0,
                        "autoAssignToTeam": True,
                        "testers": ["tester"],
                        "testsuites": {
                            "Signup": {
                                "description": "tests for user signup",
                                "useLatestVersions": False,
                                "testcases": {
                                    "Can register": {
                                        "description": "",
                                        "maxAttachmentSizeInMbytes": 0,
                                        "maxNumberOfAttachments": 0,
                                        "automationUri": "",
                                        "steps": [
                                            ("Click 'register.'",
                                             "See registration form."),
                                            ("Fill all fields and submit.",
                                             "See message and login form."),
                                            ],
                                        },
                                    "Can login": {
                                        "description": "",
                                        "maxAttachmentSizeInMbytes": 0,
                                        "maxNumberOfAttachments": 0,
                                        "automationUri": "",
                                        "steps": [
                                            ("Click 'login.'",
                                             "See login form."),
                                            ("Fill username/pw and submit.",
                                             "See welcome message with name."),
                                            ],
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            "Test Cycle 2": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 2",
                "testruns": {},
                },
            "Test Cycle 3": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 2",
                "testruns": {},
                },
            "Test Cycle 4": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 2",
                "testruns": {},
                },
            "Test Cycle 5": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 2",
                "testruns": {},
                },
            "Test Cycle 6": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 2",
                "testruns": {},
                },
            "Test Cycle 7": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 2",
                "testruns": {},
                },
            "Test Cycle 8": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 2",
                "testruns": {},
                },
            "Test Cycle 9": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 2",
                "testruns": {},
                },
            "Test Cycle 10": {
                "startDate": datetime.date.today(),
                "description": "Test Cycle 2",
                "testruns": {},
                },
            },
        },
    }



USERS = [
    {
        "firstName": "Tester",
        "lastName": "McTesterson",
        "screenName": "tester",
        "email": "tester@example.com",
        "password": "testpw",
        },
    {
        "firstName": "Tester2",
        "lastName": "McTester2son",
        "screenName": "tester2",
        "email": "tester2@example.com",
        "password": "testpw",
        },
    ]

MANAGERS = [
    {
        "firstName": "Manager",
        "lastName": "McManager",
        "screenName": "manager",
        "email": "manager@example.com",
        "password": "testpw",
        },
    {
        "firstName": "Manager2",
        "lastName": "McManager2",
        "screenName": "manager2",
        "email": "manager2@example.com",
        "password": "testpw",
        },
    ]

ADMINS = [
    {
        "firstName": "Admin",
        "lastName": "McAdmin",
        "screenName": "admin",
        "email": "admin@example.com",
        "password": "testpw",
        },
    {
        "firstName": "Admin2",
        "lastName": "McAdmin2",
        "screenName": "admin2",
        "email": "admin2@example.com",
        "password": "testpw",
        },
    ]


class Command(BaseCommand):
    help = ("Create a set of test data useful for experimenting with the TCM.")
    args = '[<admin role ID>]'

    def handle(self, *args, **options):
        try:
            ADMIN_ROLE_ID = int(args[0])
        except IndexError:
            ADMIN_ROLE_ID = None
        except ValueError:
            raise CommandError("Optional arg should be integer admin role ID")

        try:
            MANAGER_ROLE_ID = int(args[1])
        except IndexError:
            MANAGER_ROLE_ID = None
        except ValueError:
            raise CommandError(
                "Optional second arg should be integer manager role ID")

        company = Company.get("companies/%s" % conf.CC_COMPANY_ID, auth=admin)

        environments = {}
        environmenttypes = {}
        for name, envs in ENVIRONMENTS["types"].items():
            et = EnvironmentType(name=name, company=company, groupType=False)
            EnvironmentTypeList.get(auth=admin).post(et)
            print "Created environment type '%s.'" % name
            environmenttypes[name] = et

            for name in envs:
                e = Environment(name=name, company=company, environmentType=et)
                EnvironmentList.get(auth=admin).post(e)
                print "Created environment '%s.'" % name
                environments[name] = e

        environmentgrouptypes = {}
        grouptypelists = {}
        for name, types in ENVIRONMENTS["grouptypes"].items():
            egt = EnvironmentType(name=name, company=company, groupType=True)
            EnvironmentTypeList.get(auth=admin).post(egt)
            print "Created environment group type '%s.'" % name
            environmentgrouptypes[name] = egt

            envs = []
            for t in types:
                envs.extend([environments[n] for n in ENVIRONMENTS["types"][t]])

            envgroups = company.autogenerate_env_groups(envs, egt)
            grouptypelists[name] = envgroups

        users = {}
        for data in USERS:
            user = User(company=company, **data)
            UserList.get(auth=admin).post(user)
            user.roles = [conf.CC_NEW_USER_ROLE_ID]
            user.activate()
            print "Created user '%s.'" % user.screenName
            users[data["screenName"]] = user

        if MANAGER_ROLE_ID is not None:
            managers = {}
            for data in MANAGERS:
                user = User(company=company, **data)
                UserList.get(auth=admin).post(user)
                user.roles = [MANAGER_ROLE_ID]
                user.activate()
                print "Created manager user '%s.'" % user.screenName
                managers[data["screenName"]] = user

        if ADMIN_ROLE_ID is not None:
            admins = {}
            for data in ADMINS:
                user = User(company=company, **data)
                UserList.get(auth=admin).post(user)
                user.roles = [ADMIN_ROLE_ID]
                user.activate()
                print "Created admin user '%s.'" % user.screenName
                admins[data["screenName"]] = user

        cc = Credentials(USERS[0]["email"], password=USERS[0]["password"])

        products = {}
        for name, data in PRODUCTS.items():
            testers = data.pop("testers", [])
            egt_name = data.pop("environments")
            cycles = data.pop("cycles", {})
            envs = grouptypelists[egt_name]
            p = Product(name=name, company=company, **data)
            ProductList.get(auth=admin).post(p)
            p.environmentgroups = envs
            p = p.refresh()
            if testers: p.team = [users[u] for u in testers]
            print "Created product '%s.'" % name
            products[name] = p

            for name, data in cycles.items():
                testruns = data.pop("testruns", {})
                testers = data.pop("testers", [])
                tc = TestCycle(name=name, product=p, **data)
                TestCycleList.get(auth=admin).post(tc)
                tc.activate()
                if testers: tc.team = [users[u] for u in testers]
                print "Created test cycle '%s.'" % name

                for name, data in testruns.items():
                    suites = data.pop("testsuites")
                    testers = data.pop("testers", [])
                    tr = TestRun(testCycle=tc, name=name, **data)
                    TestRunList.get(auth=admin).post(tr)
                    print "Created test run '%s.'" % name

                    for name, data in suites.items():
                        cases = data.pop("testcases")
                        ts = TestSuite(
                            name=name, company=company, product=p, **data)
                        TestSuiteList.get(auth=admin).post(ts)
                        print "Created test suite '%s.'" % name

                        for name, data in cases.items():
                            steps = data.pop("steps")
                            case = TestCaseVersion(product=p, name=name, **data)
                            TestCaseList.get(auth=cc).post(case)
                            print "Created test case '%s.'" % name

                            for (i, (instruction, result)) in enumerate(steps):
                                step = TestCaseStep(
                                    name="step %s" % i,
                                    testCaseVersion=case,
                                    instruction=instruction,
                                    expectedResult=result,
                                    stepNumber=i+1,
                                    estimatedTimeInMin=0)
                                case.steps.post(step)

                            case.approve(auth=admin)
                            case.activate(auth=admin)
                            ts.addcase(case)

                        ts.activate()
                        tr.addsuite(ts)

                    tr.activate()
                    if testers: tr.team = [users[u] for u in testers]
