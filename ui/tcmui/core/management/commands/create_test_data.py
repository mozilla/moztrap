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
from ....testcases.models import TestCaseVersion, TestCaseList, TestCaseStep
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
        "cycles": {
            "Test Cycle 1": {
                "startDate": datetime.date.today(),
                "description": "",
                "testruns": {
                    "Test Run 1A": {
                        "startDate": datetime.date.today(),
                        "selfAssignAllowed": True,
                        "selfAssignLimit": 0,
                        "autoAssignToTeam": True,
                        "testcases": {
                            "Can register": {
                                "description": "",
                                "maxAttachmentSizeInMbytes": 0,
                                "maxNumberOfAttachments": 0,
                                "steps": [
                                    ("Click 'register.'",
                                     "See registration form."),
                                    ("Fill all fields and submit.",
                                     "See success message and login form."),
                                    ],
                                },
                            "Can login": {
                                "description": "",
                                "maxAttachmentSizeInMbytes": 0,
                                "maxNumberOfAttachments": 0,
                                "steps": [
                                    ("Click 'login.'",
                                     "See login form."),
                                    ("Fill username and password and submit.",
                                     "See welcome message with name."),
                                    ],
                                },
                            },
                        },
                    },
                },
            },
        },
    }



USERS = [
    {
        "firstName": "Some",
        "lastName": "Tester",
        "screenName": "tester",
        "email": "tester@example.com",
        "password": "testpw",
        },
    ]

ADMINS = [
    {
        "firstName": "The",
        "lastName": "Admin",
        "screenName": "admin",
        "email": "admin@example.com",
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

        company = Company.get("companies/%s" % conf.TCM_COMPANY_ID, auth=admin)

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

            grouptypelists[name] = envs

        users = []
        for data in USERS:
            user = User(company=company, **data)
            UserList.get(auth=admin).post(user)
            user.roles = [conf.TCM_NEW_USER_ROLE_ID]
            user.activate()
            print "Created user '%s.'" % user.screenName
            users.append(user)

        if ADMIN_ROLE_ID is not None:
            admins = []
            for data in ADMINS:
                user = User(company=company, **data)
                UserList.get(auth=admin).post(user)
                user.roles = [ADMIN_ROLE_ID]
                user.activate()
                print "Created admin user '%s.'" % user.screenName
                admins.append(user)

        cc = Credentials(USERS[0]["email"], password=USERS[0]["password"])

        products = {}
        for name, data in PRODUCTS.items():
            egt_name = data.pop("environments")
            cycles = data.pop("cycles", {})
            egt = environmentgrouptypes[egt_name]
            envs = grouptypelists[egt_name]
            p = Product(name=name, company=company, **data)
            ProductList.get(auth=admin).post(p)
            p.autogenerate_env_groups(envs, egt)
            print "Created product '%s.'" % name
            products[name] = p

            for name, data in cycles.items():
                testruns = data.pop("testruns", {})
                tc = TestCycle(name=name, product=p, **data)
                TestCycleList.get(auth=admin).post(tc)
                print "Created test cycle '%s.'" % name

                tc.activate()

                for name, data in testruns.items():
                    cases = data.pop("testcases")
                    tr = TestRun(testCycle=tc, name=name, **data)
                    TestRunList.get(auth=admin).post(tr)
                    print "Created test run '%s.'" % name

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
                        tr.addcase(case)

                    tr.activate()
