'''
Created on Oct 7, 2010

@author: camerondawson
'''
from lettuce import *
from step_helper import *
from steps_companies import *
import httplib
import mock_scenario_data

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

@after.all
def teardown_after_all(total):
    if (world.restore_db_after_all):
        restore_db_state()

@before.each_scenario
def setup_before_scenario(scenario):
    if (world.restore_db):
        restore_db_state()
        
    if (world.setup_seed_data):
        setup_seed_data()

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
    company = world.seed_company
    world.names["company"] = company["name"]

    #TODO: not able to search for the country name yet    
    company["countryId"] = 123
    if company.has_key("country name"):
        del company["country name"]

    do_post(world.path_companies, 
            company)
    
    # create the seed product
    # persist the last one we make.  Sometimes we will only make one.
    product = world.seed_product
    world.names["product"] = product["name"]
    
    # get the company id from the passed company name
    company_id, version = get_company_resid(product["company name"])
    product["companyId"] = company_id 
    if product.has_key("company_name"):
        del product["company name"]

    do_post(world.path_products, 
            product)
    


# creates a company and product that is used for many of the tests
def setup_seed_data():
    pass
   
@before.each_step
def setup_step_connection(step):
    setup_connection() 

    










