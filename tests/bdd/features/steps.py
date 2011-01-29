'''
Created on Oct 7, 2010

@author: camerondawson
'''
from lettuce import *
#from numpy.ma.testutils import *
from step_helper import *
from step_helper import jstr, add_params
import httplib
import mock_scenario_data
import post_data
import time

def save_db_state():
    '''
        This will dump the database to a file.  That file will then be used at the beginning
        of each scenario to reset to a known state of the database
        
        sudo mysqldump > db_clean.sql
    '''
    conn = httplib.HTTPConnection(world.hostname, world.port, timeout=50)
    conn.request("GET", world.path_savedb)
    data = conn.getresponse()

def restore_db_state():
    '''
        This will re-create the database from the dump created in save_db_state().  This will
        be run at the beginning end of each scenario to reset the database to the known state.
        
        sudo mysql < db_clean.sql
    '''
    conn = httplib.HTTPConnection(world.hostname, world.port, timeout=50)
    conn.request("GET", world.path_restoredb)
    response = conn.getresponse()
    verify_status(200, response, "Restored the database")
    
def setup_connection():
    world.conn = httplib.HTTPConnection(world.hostname, world.port) 


@before.all
def setup_before_all():
    if (world.save_db):
        save_db_state()


# DATA SETUP
# This is the function that uploads the expected data to the mock server.
#
# @todo Need to make this only run in DEBUG mode or something
@before.each_scenario
def setup_before_scenario(scenario):
    if (world.restore_db):
        restore_db_state()

    if (world.use_mock):
        scenarioData = mock_scenario_data.get_scenario_data(scenario.name).strip() 
    
        headers = {'content-Type':'text/plain',
                   "Content-Length": "%d" % len(scenarioData) }
    
        setup_connection()
        world.conn.request("POST", add_params(world.path_mockdata, {"scenario" : scenario.name}), "", headers)
    
        world.conn.send(scenarioData)
        world.conn.getresponse()

#@after.each_scenario
def restore_db(scenario):
    restore_db_state()
    
@before.each_step
def setup_step_connection(step):
    setup_connection() 

    

'''
######################################################################

                     COMPANY STEPS

######################################################################
'''

@step(u'company with name "(.*)" (does not exist|exists)')
def check_company_foo_existence(step, company_name, existence):
    search_and_verify_existence(step, world.path_companies, 
                    {"name": company_name}, 
                    "company", existence)


@step(u'add a new company with name "(.*)"')
def add_a_new_company_with_name_foo(step, company_name):
    post_payload = post_data.get_submit_company_params(company_name)
    headers = {'Authorization': get_auth_header()}

    world.conn.request("POST", add_params(world.path_companies, post_payload), "", headers)
    #world.conn.send(post_payload)
    response = world.conn.getresponse()
    verify_status(200, response, "create new company")

@step(u'search all Companies')
def search_all_companies(step):
    assert False, 'This step must be implemented'


'''
######################################################################

                     ATTACHMENT STEPS

######################################################################
'''


@step(u'upload attachment with filename "(.*)" to test case with name "(.*)"')
def upload_attachment_foo_to_test_case_bar(step, attachment, test_case):
    test_case_id, version = get_test_case_resid(test_case)

    content_type, body = encode_multipart_formdata([], [{'key': attachment, 
                                                         'filename': attachment, 
                                                         'value': open(world.testfile_dir + attachment, 'rb')}])

    headers = {"Accept": "application/xml", 
               "Content-Type":content_type,
               "Content-Length": "%d" % len(body) }

    world.conn.request("POST", 
                       add_params(world.path_testcases + test_case_id + "/attachments/upload", 
                                  {"originalVersionId": version}), 
                       body, headers)

    response = world.conn.getresponse()
    verify_status(200, response, "upload attachment with filename")
    








