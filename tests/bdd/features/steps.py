'''
Created on Oct 7, 2010

@author: camerondawson
'''
from lettuce import *
from step_helper import *
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
def teardown_after_all():
    if (world.restore_db_after_all):
        restore_db_state()

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

   
@before.each_step
def setup_step_connection(step):
    setup_connection() 

    










