'''
Created on Nov 16, 2010

@author: camerondawson
'''
from lettuce import world

world.applicationUnderTest = "Case Keeper"
world.hostname = "camd.mv.mozilla.com"

# for my servlet
world.port = 8080
# for the rails app
#world.port = 3000

# whether or not to send mock data to the server before each scenario.
# don't do this when using a real web server.  Shouldn't cause tests to fail,
# but it will make the logs verbose with errors.
world.use_mock = False
#world.use_mock = True

world.save_db = False
world.restore_db = True

# the namespace used to prefix every field
world.ns = 'ns1.'

#used to find data, such as sample files for upload
world.testfile_dir = "./data/"

#prefix to uri pathing
world.api_prefix = "/tcm/services/v2/rest/"

# URI namespace path map
world.path_companies =          world.api_prefix + "companies/"
world.path_environmentgroups =  world.api_prefix + "environmentgroups/"
world.path_environments =       world.api_prefix + "environments/"
world.path_environmenttypes =   world.api_prefix + "environmenttypes/"

world.env_path_map = {"environments":      world.path_environments,
                      "environment":       world.path_environments,
                      "environmenttypes":  world.path_environmenttypes,
                      "environmenttype":   world.path_environmenttypes,
                      "environmentgroups": world.path_environmentgroups,
                      "environmentgroup":  world.path_environmentgroups}

world.path_tags =               world.api_prefix + "tags/"

world.path_login =              world.api_prefix + "users/login/"
world.path_logout =             world.api_prefix + "users/logout/"
world.path_permissions =        world.api_prefix + "users/permissions/"
world.path_roles =              world.api_prefix + "users/roles/"
world.path_users =              world.api_prefix + "users/"
world.path_users_activation =   world.api_prefix + "users/%s/%s"

world.path_testcases =          world.api_prefix + "testcases/"
world.path_testcycles =         world.api_prefix + "testcycles/"
world.path_testruns =           world.api_prefix + "testruns/"
world.path_testsuites =         world.api_prefix + "testsuites/"
world.path_products =           world.api_prefix + "products/"

# paths for test automation
world.path_mockdata =           "/mockdata"
world.path_savedb =             "/TcmDbUnitServlet/savedb"
world.path_restoredb =          "/TcmDbUnitServlet/restoredb"

# dict of names of objects used in scenarios to remember from one step to the next
world.names = {}