'''
Created on Oct 7, 2010

@author: camerondawson
'''
from lettuce import *
from step_helper import *
from steps_companies import *
from steps_users import *
import httplib
import mock_scenario_data
import pprint
import cgi

def save_db_state():
    '''
        This will dump the database to a file.  That file will then be used at the beginning
        of each scenario to reset to a known state of the database
    '''
    conn = httplib.HTTPConnection(world.hostname, world.port, timeout=120)
    conn.request("GET", world.path_savedb)
    conn.getresponse()

def restore_db_state():
    '''
        This will re-create the database from the dump created in save_db_state().  This will
        be run at the beginning end of each scenario to reset the database to the known state.
    '''
    conn = httplib.HTTPConnection(world.hostname, world.port, timeout=120)
    conn.request("GET", world.path_restoredb)
    response = conn.getresponse()
    verify_status(200, response, "Restored the database")
    
def setup_connection():
    world.conn = httplib.HTTPConnection(world.hostname, world.port) 


@before.all
def setup_before_all():
    if (world.save_db):
        save_db_state()

    # dict of names of objects used in scenarios to remember from one step to the next
    world.names = {}

    ################################
    # paths relative to the namespace        
    ################################
    
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
            
    ################################
    # setup objects
    ################################
    
    # usually, the test will replace the countryId based on looking it up
    world.seed_company = {"name": "Massive Dynamic",
                          "phone": "555-867-5309",
                          "address": "650 Castro St.",
                          "city": "Mountain View",
                          "zip": "94043",
                          "url": "http//www.fringepedia.net",
                          "country name": "United States"
                          }
    
    # usually the test setup will replace the companyId with the one looked up based on creating
    # the seed company above.
    world.seed_product = {"company name": "Massive Dynamic",
                          "name": "Cortexiphan",
                          "description": "I can see your universe from here"
                          }
    
    # keep track of the api(uri) calls made
    world.apis_called = {}

@after.all
def teardown_after_all(total):
    if (world.restore_db_after_all):
        restore_db_state()
    
    write_apis_called_file()


def write_apis_called_file():
    
#    pp = pprint.PrettyPrinter(indent=4)
#    output = pp.pformat(world.apis_called)
    # write out api calls by sentence
    f = open(world.apis_called_file, 'w')
    
    world.apis_called
    
    tablerows = ""
    # we can't sort a dict, so we need to sort the keys, then fetch the value for it
    keys = world.apis_called.keys()
    keys.sort()
    for key in keys:
        # each value is a set of the methods called (to keep them unique) so we join them by spaces
        tablerow = "<tr><td>%s</td><td>%s</td></tr>" % (key, ' '.join(world.apis_called[key]))
        tablerows += tablerow

    output = '''
            <html xmlns="http://www.w3.org/1999/xhtml">
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                    
                    <title>%(appUnderTest)s Results</title>
                </head>
                <body>
                    <h1>%(appUnderTest)s APIs Called</h1>
                    <table border=1>
                    <tr><th>API</th><th>Methods</th></tr>
                    %(tablerows)s
                    </table>
                </body>
            </html>
        ''' % {'tablerows': tablerows,
               'appUnderTest': cgi.escape(world.applicationUnderTest)
               }
    
    
    f.write(output)
    
    # write out just the unique apis that were called
    
#    api_set = set([obj[0] for obj in mylistofobjs])
    
#    f = open(world.api_calls_file, 'w')
#    f.write(jstr(world.apis_by_sentence))
    

@before.each_scenario
def setup_before_scenario(scenario):
    if (world.restore_db):
        restore_db_state()
        
    if (world.use_mock):
        scenarioData = mock_scenario_data.get_scenario_data(scenario.name).strip() 
    
        headers = {'content-Type':'text/plain',
                   "Content-Length": "%d" % len(scenarioData) }
    
        setup_connection()
        world.conn.request("POST", 
                           add_params(world.path_mockdata, 
                                      {"scenario" : scenario.name}), 
                            "", headers)
    
        world.conn.send(scenarioData)
        world.conn.getresponse()

@step(u'create the seed company and product')
def create_seed_company_and_product(step):
    
    # create the seed company
#    step.given('''
#        create the following new companies:
#            | name    | phone     | address     | city     | zip     | url     | country name     |
#            |%(name)s | %(phone)s | %(address)s | %(city)s | %(zip)s | %(url)s | %(country name)s |
#    ''' % world.seed_company)


    # create the seed company    
    company = world.seed_company.copy()
    world.names["company"] = company["name"]

    #TODO: not able to search for the country name yet    
    company["countryId"] = 123
    if company.has_key("country name"):
        del company["country name"]

    do_post(world.path_companies, 
            company)
    
    # create the seed product
    # persist the last one we make.  Sometimes we will only make one.
    product = world.seed_product.copy()
    world.names["product"] = product["name"]
    
    # get the company id from the passed company name
    company_id = get_company_resid(product["company name"])[0]
    product["companyId"] = company_id 
    if product.has_key("company name"):
        del product["company name"]

    do_post(world.path_products, 
            product)
    

@before.each_step
def setup_step_connection(step):
    setup_connection() 

    world.current_sentence = step.sentence










