'''
Created on Nov 16, 2010

@author: camerondawson

This class contains settings that may be specific to the deployment of
the tests and/or the Tcm Platform

'''
from lettuce import world

world.applicationUnderTest = "Case Keeper"
world.hostname = "localhost"

world.db_hostname = world.hostname

# for my servlet
world.port = 8080

# whether or not to send mock data to the server before each scenario.
# don't do this when using a real web server.  Shouldn't cause tests to fail,
# but it will make the logs verbose with errors.
world.use_mock = False
#world.use_mock = True

# whether or not to save the database for restoration before any tests are executed.
# generally a good idea on the Hudson deployment.
# generally NOT what you want when developing and debugging tests.  Especially true
# if you don't have restore_db_after_all set to True, because you may end up saving a
# non-clean state.
world.save_db = True

# whether or not to restore the DB between each scenario.
# generally a good idea in general
world.restore_db = True

# whether or not to restore the DB to default state after all tests were run.
# generally a good idea on the Hudson deployment.
# generally NOT what you want when developing and debugging tests.
world.restore_db_after_all = True

# the namespace used to prefix every field
world.ns = 'ns1.'

#used to find data, such as sample files for upload
world.testfile_dir = "./data/"

# this file is a listing of all unique api calls made in this test
world.apis_called_file = 'apis_called.html'

#prefix to uri pathing
world.api_prefix = "/tcm/services/v2/rest/"


# paths for test automation
world.path_mockdata =           "/mockdata"
world.path_savedb =             "/TcmDbUnitServlet/savedb?host=%s" % (world.db_hostname)
world.path_restoredb =          "/TcmDbUnitServlet/restoredb?host=%s" % (world.db_hostname)

# now import the "local" file for any user-changed settings
try:
    import terrain_local
except:
    # if it doesn't exist, just use all these default values
    pass


