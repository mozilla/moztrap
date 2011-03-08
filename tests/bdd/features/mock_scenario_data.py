############################################################################
'''

                           MOCK DATA GENERATOR

############################################################################
This library is used to generate the data that is sent to the mock servlet so it
can return it.  Each list item is returned for every call made.  Sometimes more than one
call is made per step, so watch out for that.  This is often a preliminary call to get
the resourceIdentity for a user, role, permission, etc.

Created on Oct 18, 2010

@author: camerondawson
'''

from lettuce import world
from tcm_data_helper import plural
import json
import urllib

def get_scenario_data(scenarioName):
    '''
        Get scenario data, keyed off the scenarioName passed in.  If the text of the scenario changes,
        then it won't find anything, so be careful.

        I added a "comment" field to each element to help me keep track of what each call response was expected to respond to.
        I don't use it in the mock servlet at all.  It's purely for documentation here.  But since the objects are in block
        quotes, this was the best I could come up with.  Perhaps I'll use it.  Optional for now, really.

        TODO: There may be a better way to do this, but this is the best I could come up with.  Perhaps it's genius.
        It's simple, anyway.  I'm just concerned with how well it will scale.
    '''

    steps = None
    if scenarioName == "Register a new user":
        steps = \
            [
               {"comment": "User does not exist",
                "request": world.api_prefix + "users?firstName=Jedi&lastName=Jones",
                "response": "No response expected",
                "status": "404"
                },
               {"comment": "Posting the user data",
                "request": world.api_prefix + "users",
                "response": "POST, w/o response",
                "status": "200"
                },
               {"comment": "Check user exists, but not active",
                "request": world.api_prefix + "users?firstName=Jedi&lastName=Jones",
                "response": as_resp(as_sr(get_returned_users(["Jedi Jones"], "false"))),
                "status": "200"
                },
               {"comment": "request it to be activated",
                "request": world.api_prefix + "users?firstName=Jedi&lastName=Jones",
                "response": as_resp(as_sr(get_returned_users(["Jedi Jones"], "false"))),
                "status": "200"
                },
               {"comment": "expect it's now active",
                "request": world.api_prefix + "users?firstName=Jedi&lastName=Jones",
                "response": as_resp(as_sr(get_returned_users(["Jedi Jones"], "true"))),
                "status": "200"
                }
            ]

    elif scenarioName == "Activate a Non Active user":
        steps = \
            [
                {"comment": "check user registered",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=NotActive",
                 "response": as_resp(as_sr(get_returned_users(["Jedi NotActive"], "false"))),
                 "status": "200"
                 },
                {"comment": "get user id",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=NotActive",
                 "response": as_resp(as_sr(get_returned_users(["Jedi NotActive"], "false"))),
                 "status": "200"
                 },
                {"comment": "check user active status false",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=NotActive",
                 "response": as_resp(as_sr(get_returned_users(["Jedi NotActive"], "false"))),
                 "status": "200"
                 },
                {"comment": "set user active",
                 "request": world.api_prefix + "users/8/activate",
                 "response": "POST, no return",
                 "status": "200"
                 },
                {"comment": "check user active status true",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=NotActive",
                 "response": as_resp(as_sr(get_returned_users(["Jedi NotActive"], "true"))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Deactivate an Active user":
        steps = \
            [
                {"comment": "check user registered",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Active",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Active"], "true"))),
                 "status": "200"
                 },
                {"comment": "get user id",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Active",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Active"], "true"))),
                 "status": "200"
                 },
                {"comment": "check user active status true",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Active",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Active"], "true"))),
                 "status": "200"
                 },
                {"comment": "set user deactivated",
                 "request": world.api_prefix + "users/8/activate",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "check user active status false",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Active",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Active"], "false"))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Create a new Role and add Permission":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Jedi Admin"], "true")),
                 "status": "200"
                 },
                {"comment": "get id of user",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Admin",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Admin"], "true"))),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["ADMINISTRATOR"]))),
                 "status": "200"
                 },
                {"comment": "create a new role",
                 "request": world.api_prefix + "roles",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "get id of role",
                 "request": world.api_prefix + "roles?description=Creationator",
                 "response": as_resp(as_sr(get_returned_roles(["Creationator"]))),
                 "status": "200"
                 },
                {"comment": "add permission to role",
                 "request": world.api_prefix + "roles/24/permissions",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "get id of role",
                 "request": world.api_prefix + "roles?description=Creationator",
                 "response": as_resp(as_sr(get_returned_roles(["Creationator"]))),
                 "status": "200"
                 },
                {"comment": "get permissions for new role",
                 "request": world.api_prefix + "roles/24/permissions",
                 "response": as_resp(as_sr(get_returned_permissions(["Spammer"]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Get list of roles":
        steps = \
            [
                {"comment": "get list of roles",
                 "request": world.api_prefix + "roles"                   ,
                 "response": as_resp(as_sr(get_returned_roles(["Apple", "Zipper", "Frame"]))),
                 "status": "200"
                 },
                {"comment": "get list of ASC roles",
                 "request": world.api_prefix + "roles?sortDirection=ASC" ,
                 "response": as_resp(as_sr(get_returned_roles(["Apple", "Frame", "Zipper"]))),
                 "status": "200"
                 },
                {"comment": "get list of DESC roles",
                 "request": world.api_prefix + "roles?sortDirection=DESC",
                 "response": as_resp(as_sr(get_returned_roles(["Zipper", "Frame", "Apple"]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Create a new Test Case":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Jedi Creator"], "true")),
                 "status": "200"
                 },
                {"comment": "get id of user",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Creator",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Creator"], "true"))),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["TEST_CREATOR"]))),
                 "status": "200"
                 },
                {"comment": "create a new test case",
                 "request": world.api_prefix + "testcases",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "get new test case data",
                 "request": world.api_prefix + "testcases?description=Testing%20mic%20%231.%20%20Isn%27t%20this%20a%20lot%20of%20fun.",
                 "response": as_resp(as_sr(get_returned_test_case(["Testing mic #1.  Isn't this a lot of fun."]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Assign a Role to a User":
        steps = \
            [
                {"comment": "Given user Jedi Roller has active status true",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Roller",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Roller"], "true"))),
                 "status": "200"
                 },
                {"comment": "And the role of CHIPPER exists",
                 "request": world.api_prefix + "roles",
                 "response": as_resp(as_sr(get_returned_roles(["CHIPPER"]))),
                 "status": "200"
                 },
                {"comment": "get id of user",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Roller",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Roller"], "true"))),
                 "status": "200"
                 },
                {"comment": "And Jedi Roller does not already have the role of CHIPPER",
                 "request": world.api_prefix + "users/8/roles"                       ,
                 "response": as_resp(as_sr(get_returned_roles(["MASHER", "SMASHER"]))),
                 "status": "200"
                 },
                {"comment": "get id of user",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Roller",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Roller"], "true"))),
                 "status": "200"
                 },
                {"comment": "When I add role of CHIPPER to user Jedi Roller",
                 "request": world.api_prefix + "users/8/roles"                       ,
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "get id of user",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Roller",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Roller"], "true"))),
                 "status": "200"
                 },
                {"comment": "Then Jedi Roller has the role of CHIPPER",
                 "request": world.api_prefix + "users/8/roles"                       ,
                 "response": as_resp(as_sr(get_returned_roles(["MASHER", "SMASHER", "CHIPPER"]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Check Roles of a User":
        steps = \
            [
                {"comment": "Given user Jedi Roller has active status true",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Roller",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Roller"], "true"))),
                 "status": "200"
                 },
                {"comment": "get id of user",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Roller",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Roller"], "true"))),
                 "status": "200"
                 },
                {"comment": "Then Jedi Roller has the role of MASHER and SMASHER",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["MASHER", "SMASHER"]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Check the Assignments of a User":
        steps = \
            [
                {"comment": "Given user has active status true",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Assigned",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Assigned"], "true"))),
                 "status": "200"
                 },
                {"comment": "get id of user",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Assigned",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Assigned"], "true"))),
                 "status": "200"
                 },
                {"comment": "Then the user has the listed assignments",
                 "request": world.api_prefix + "users/8/assignments",
                 "response": as_resp(as_sr(get_returned_assignments(["What the cat dragged in", "Where I put the keys"]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Create a new Company":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Jedi Creator"], "true")),
                 "status": "200"
                 },
                {"comment": "get id of user",
                 "request": world.api_prefix + "users?firstName=Jedi&lastName=Creator",
                 "response": as_resp(as_sr(get_returned_users(["Jedi Creator"], "true"))),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["COMPANY_CREATOR"]))),
                 "status": "200"
                 },
                {"comment": "check company does not exist",
                 "request": world.api_prefix + "companies?name=Massive%20Dynamic",
                 "response": as_resp(as_sr(get_returned_companies([]))),
                 "status": "404"
                 },
                {"comment": "create a new company",
                 "request": world.api_prefix + "companies",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "check now company exists",
                 "request": world.api_prefix + "companies?name=Massive%20Dynamic",
                 "response": as_resp(as_sr(get_returned_companies(["Massive Dynamic"]))),
                 "status": "200"
                 }
            ]


    elif scenarioName == "Environment - Creation":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Jedi Creator"], "true")),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["ENVIRONMENT_CREATOR"]))),
                 "status": "200"
                 },
                {"comment": "check environment does not exist",
                 "request": world.api_prefix + "environments?name=Walter%27s%20Lab",
                 "response": as_resp(as_sr(get_returned_environments([]))),
                 "status": "404"
                 },
                {"comment": "create a new environment",
                 "request": world.api_prefix + "environments",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "check now environment exists",
                 "request": world.api_prefix + "environments?name=Walter%27s%20Lab",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Environment - Add to Product":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Jedi Creator"], "true")),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["PRODUCT_EDITOR"]))),
                 "status": "200"
                 },
                {"comment": "check environment exists",
                 "request": world.api_prefix + "environments?name=Walter%27s%20Lab",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 },
                {"comment": "check product exists",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_products(["Continuum Transfunctioner"]))),
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_products(["Continuum Transfunctioner"]))),
                 "status": "200"
                 },
                {"comment": "check environment is not added to product",
                 "request": world.api_prefix + "products/8/environments/",
                 "response": as_resp(as_sr(get_returned_environments([]))),
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_products(["Continuum Transfunctioner"]))),
                 "status": "200"
                 },
                {"comment": "add environment to product",
                 "request": world.api_prefix + "products/8/environments",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_products(["Continuum Transfunctioner"]))),
                 "status": "200"
                 },
                {"comment": "check now environment is added to product",
                 "request": world.api_prefix + "products/8/environments/",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Environment - Remove from Product":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Jedi Creator"], "true")),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["PRODUCT_EDITOR"]))),
                 "status": "200"
                 },
                {"comment": "check environment exists",
                 "request": world.api_prefix + "environments?name=Walter%27s%20Lab",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 },
                {"comment": "check product exists",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_products(["Continuum Transfunctioner"]))),
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_products(["Continuum Transfunctioner"]))),
                 "status": "200"
                 },
                {"comment": "check environment is not added to product",
                 "request": world.api_prefix + "products/8/environments/",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_products(["Continuum Transfunctioner"]))),
                 "status": "200"
                 },
                {"comment": "get id of environment",
                 "request": world.api_prefix + "environments?name=Walter%27s%20Lab",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 },
                {"comment": "remove environment from product",
                 "request": world.api_prefix + "products/8/environments",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_products(["Continuum Transfunctioner"]))),
                 "status": "200"
                 },
                {"comment": "check now environment is added to product",
                 "request": world.api_prefix + "products/8/environments/",
                 "response": as_resp(as_sr(get_returned_environments([]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Environment - Add to Test Case":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Jedi Creator"], "true")),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["TEST_EDITOR"]))),
                 "status": "200"
                 },
                {"comment": "check environment exists",
                 "request": world.api_prefix + "environments?name=Walter%27s%20Lab",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 },
                {"comment": "check product exists",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_test_case(["Wazzon Chokey?"]))),
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_test_case(["Wazzon Chokey?"]))),
                 "status": "200"
                 },
                {"comment": "check environment is not added to product",
                 "request": world.api_prefix + "products/8/environments/",
                 "response": as_resp(as_sr(get_returned_environments([]))),
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_test_case(["Wazzon Chokey?"]))),
                 "status": "200"
                 },
                {"comment": "add environment to product",
                 "request": world.api_prefix + "products/8/environments",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_test_case(["Wazzon Chokey?"]))),
                 "status": "200"
                 },
                {"comment": "check now environment is added to product",
                 "request": world.api_prefix + "products/8/environments/",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Environment - Remove from Test Case":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Jedi Creator"], "true")),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["TEST_EDITOR"]))),
                 "status": "200"
                 },
                {"comment": "check environment exists",
                 "request": world.api_prefix + "environments?name=Walter%27s%20Lab",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 },
                {"comment": "check product exists",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_test_case(["Wazzon Chokey?"]))),
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_test_case(["Wazzon Chokey?"]))),
                 "status": "200"
                 },
                {"comment": "check environment is not added to product",
                 "request": world.api_prefix + "products/8/environments/",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_test_case(["Wazzon Chokey?"]))),
                 "status": "200"
                 },
                {"comment": "get id of environment",
                 "request": world.api_prefix + "environments?name=Walter%27s%20Lab",
                 "response": as_resp(as_sr(get_returned_environments(["Walter's Lab"]))),
                 "status": "200"
                 },
                {"comment": "remove environment from product",
                 "request": world.api_prefix + "products/8/environments",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "get id of product",
                 "request": world.api_prefix + "products?name=Continuum%20Transfunctioner",
                 "response": as_resp(as_sr(get_returned_test_case(["Wazzon Chokey?"]))),
                 "status": "200"
                 },
                {"comment": "check now environment is removed from product",
                 "request": world.api_prefix + "products/8/environments/",
                 "response": as_resp(as_sr(get_returned_environments([]))),
                 "status": "200"
                 }
            ]

    elif scenarioName == "Environment Type - Creation":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Jedi Creator"], "true")),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["ENVIRONMENT_CREATOR"]))),
                 "status": "200"
                 },
                {"comment": "check environment type does not exist",
                 "request": world.api_prefix + "environmenttypes?name=Laboratory",
                 "response": as_resp(as_sr(get_returned_environment_type([]))),
                 "status": "404"
                 },
                {"comment": "create a new environment type",
                 "request": world.api_prefix + "environmenttypes",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "check now environment type exists",
                 "request": world.api_prefix + "environmenttypes?name=Laboratory",
                 "response": as_resp(as_sr(get_returned_environment_type(["Laboratory"]))),
                 "status": "200"
                 }
            ]



    elif scenarioName == "Upload a new Attachment to a test case":
        steps = \
            [
                {"comment": "logged in as user",
                 "request": world.api_prefix + "users/current",
                 "response": as_resp(get_returned_users(["Olivia Dunham"], "true")),
                 "status": "200"
                 },
                {"comment": "check users roles",
                 "request": world.api_prefix + "users/8/roles",
                 "response": as_resp(as_sr(get_returned_roles(["ATTACHER"]))),
                 "status": "200"
                 },
                {"comment": "check test case exists",
                 "request": world.api_prefix + "testcases?name=Trans-Universe%20Communication",
                 "response": as_resp(as_sr(get_returned_test_case(["Trans-Universe Communication"]))),
                 "status": "200"
                 },
                {"comment": "get id of test case",
                 "request": world.api_prefix + "testcases?name=Trans-Universe%20Communication",
                 "response": as_resp(as_sr(get_returned_test_case(["Trans-Universe Communication"]))),
                 "status": "200"
                 },
                {"comment": "upload a new attachment",
                 "request": world.api_prefix + "testcases/123/attachments/upload",
                 "response": "POST, w/o response",
                 "status": "200"
                 },
                {"comment": "get id of test case",
                 "request": world.api_prefix + "testcases?name=Trans-Universe%20Communication",
                 "response": as_resp(as_sr(get_returned_test_case(["Trans-Universe Communication"]))),
                 "status": "200"
                 },
                {"comment": "check now environment type exists",
                 "response": as_resp(as_sr(get_returned_attachments(["Selectric251.txt"]))),
                 "status": "200"
                 }
            ]

    data = json.dumps(steps)
    return data


'''
############################################################################

                           HELPERS

############################################################################

'''


def as_sr(object):
    '''
        Return this object as a searchResult object
    '''
    type = object.keys()[0]
    return_value = {
        "searchResult": {
            "@xsi.type": "searchResult",
            plural(type): object
        }
    }
    return return_value


def as_resp(object):
    '''
        shortcut to make an object ready to push up as a response
    '''
    return urllib.quote(json.dumps(object))



'''
############################################################################

                           RETURN TYPES

############################################################################

'''


def get_returned_users(item_names, active, resid=7, is_search_result = False):
    '''
        Return a list of users.  It increments the resid for each one.  They're all the same
        value of "active" for now.  May need to change that in the future.
    '''

    def each_item(item, resid, active):
        name_parts = item.split()
        fname = name_parts[0]
        lname = name_parts[1]
        resid = resid + 1

        obj = {
                "firstname":fname,
                "lastname":lname,
                "email":fname + lname + "@utest.com",
                "loginname":fname + lname,
                "password":fname + lname + "123",
                "companyid":1,
                "communitymember":"false",
                "active":active,
                "resourceIdentity":get_resource_identity(resid),
                "timeline":get_timeline()
        }
        return obj
    return build_object("user", each_item, item_names, resid, active)

def get_returned_roles(items):
    def each_item(item, resid, active):
        obj = {
                "description": item,
                "resourceIdentity": get_resource_identity(24),
                "timeline": get_timeline()
        }
        return obj
    return build_object("role", each_item, items)


def get_returned_assignments(assignment_names):
    return get_returned_test_case(assignment_names)


def get_returned_permissions(items):
    def each_item(item, resid, active):
        obj = {
                "description": item,
                "resourceIdentity": get_resource_identity(24)
        }
        return obj
    return build_object("permission", each_item, items)


def get_returned_test_case(items):
    def each_item(item, resid, active):
        obj = {
                "productid":"1",
                "maxattachmentsizeinmbytes":"10",
                "maxnumberofattachments":"5",
                "name":item,
                "description":"The generic description",
                "testcasesteps":{
                    "testcasestep":{
                        "stepnumber":"1",
                        "name":"login name missing ",
                        "instruction":"don't provide login name",
                        "expectedresult":"validation message should appear",
                        "estimatedtimeinmin":"1"
                    }
                },
                "testcasestatusid":"2",
                "majorversion":"1",
                "minorversion":"1",
                "latestversion":"true",
                "resourceIdentity":get_resource_identity(8),
                "timeline":get_timeline()
        }
        return obj
    return build_object("testcase", each_item, items)


def get_returned_companies(items):
    '''
        Takes a list of company names
    '''
    def each_item(item, resid, active):
        obj = {
                "name": item,
                "phone": "617-417-0593",
                "address": "31 lakeside drive",
                "city": "Boston",
                "zip": "01721",
                "companyUrl": "http//www.utest.com",
                "resourceIdentity": get_resource_identity(5),
                "timeline": get_timeline()
        }
        return obj
    return build_object("company", each_item, items)


def get_returned_environments(items):
    '''
        Takes a list of env names
    '''
    def each_item(item, resid, active):
        obj = {
               "name": item,
               "localeCode": "en_US",
               "sortOrder": 0,
               "environementTypeId": 1,
               "resourceIdentity": get_resource_identity(007),
               "timeline": get_timeline()
        }
        return obj
    return build_object("environment", each_item, items)


def get_returned_environment_type(items):
    '''
        Takes a list of env type names
    '''
    def each_item(item, resid, active):
        obj = {
               "name": item,
               "localeCode": "en_US",
               "sortOrder": 0,
               "resourceIdentity": get_resource_identity(007),
               "timeline": get_timeline()
        }
        return obj
    return build_object("environmenttype", each_item, items)


def get_returned_attachments(items):
    '''
        Takes a list of attachment filenames
    '''
    def each_item(item, resid, active):
        obj = {
            "fileName": item,
            "fileType": "DOC",
            "fileSizeInMB": "1",
            "storageURL": "//home/docs/specs.doc",
            "entityId": "1",
            "entityTypeId": "1",
            "resourceIdentity": get_resource_identity(8),
            "timeline": get_timeline()
        }
        return obj
    return build_object("attachment", each_item, items)


def get_returned_products(items):
    '''
        Takes a list of attachment filenames
    '''
    def each_item(item, resid, active):
        obj = {
            "name": item,
            "description": "64bit version",
            "productVersion": "1.0.3",
            "companyId": "1",
            "resourceIdentity": get_resource_identity(8),
            "timeline": get_timeline()
        }
        return obj

    return build_object("product", each_item, items)


def get_resource_identity(id):
    obj = {
        "@xsi.type": "resourceIdentity",
        "id": id,
        "url": "https:\/\/just\/a\/test\/v2\/rest\/sample\/" + str(id),
        "version": 0
    }
    return obj

def get_timeline():
    obj = {
        "@xsi.type": "timeline",
        "createDate": "2010-10-18T00:00:00-04:00",
        "createdBy": 16315,
        "lastChangeDate": "2010-10-18T17:42:24-04:00",
        "lastChangedBy": 16315
    }
    return obj

def build_object(type, each_item, items, resid=24, active="true"):
    if isinstance(items, list):
        if len(items) == 1:
            result_obj = each_item(items[0], resid, active)
        else:
            result_obj = []
            for item in items:
                obj = each_item(item, resid, active)
                result_obj.append(obj)


    else:
        result_obj = each_item(items, resid, active)

    return_value = {type: result_obj}
    return return_value


