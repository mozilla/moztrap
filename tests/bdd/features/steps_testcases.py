'''
Created on Jan 28, 2011

@author: camerondawson
'''
from lettuce import *
from step_helper import *
from step_helper import jstr, add_params
#from nose.tools import *



'''
######################################################################

                     TEST CASE STEPS

######################################################################
'''

@step(u'create a new testcase with (that name|name "(.*)")')
def create_testcase_with_name_foo(step, stored, name):
    name = get_stored_or_store_testcase_name(stored, name)
    
    headers = {'Authorization': get_auth_header(),
               'content-type': "application/x-www-form-urlencoded"
               }
               
    post_payload = {"productId": 1,
                    "maxAttachmentSizeInMBytes":"10",
                    "maxNumberOfAttachments":"5",
                    "name": name,
                    "description": "Lettuce tc"
                   }
    
    world.conn.request("POST", add_params(world.path_testcases), 
                       urllib.urlencode(post_payload, doseq=True), 
                       headers)

    response = world.conn.getresponse()
    verify_status(200, response, "Create new user")



@step(u'testcase with (that name|name "(.*)") (exists|does not exist)')
def check_testcase_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_testcase_name(stored, name)
    search_and_verify_existence(step, world.path_testcases, 
                    {"name": name}, 
                     "testcase", existence)


@step(u'delete the testcase with (that name|name "(.*)")')
def delete_testcase_with_name_foo(step, stored, name):
    name = get_stored_or_store_testcase_name(stored, name)
    
    headers = {'Authorization': get_auth_header(),
               'content-type': "application/x-www-form-urlencoded"
               }

    testcase_id, version = get_testcase_resid(name)
               
    world.conn.request("DELETE", 
                       add_params(world.path_testcases + testcase_id, 
                                  {"originalVersionId": version}), "", headers)

    response = world.conn.getresponse()
    verify_status(200, response, "delete testcase")


@step(u'add environment "(.*)" to test case "(.*)"')
def add_environment_foo_to_test_case_bar(step, environment, test_case):
    # this takes 2 requests.  
    #    1: get the id of this test case
    #    2: add the environment to the test case
    
    # fetch the test case's resource identity
    test_case_id, version = get_testcase_resid(test_case)
    
    post_payload = {"name": "test environment"
                   }
    headers = {'content-Type':'text/xml',
               "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", 
                       add_params(world.path_testcases + test_case_id + "/environments", 
                                  {"originalVersionId": version}), 
                       "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    verify_status(200, response, "post new environment to test_case")

@step(u'remove environment "(.*)" from test case "(.*)"')
def remove_environment_from_test_case(step, environment, test_case):
    # fetch the test case's resource identity
    test_case_id, version = get_testcase_resid(test_case)
    environment_id = get_environment_resid(environment)
    
    world.conn.request("DELETE", 
                       add_params(world.path_testcases + test_case_id + "/environments/" + environment_id, 
                                  {"originalVersionId": version}))
    response = world.conn.getresponse()
    verify_status(200, response, "delete new environment from test case")

@step(u'test case "(.*)" (has|does not have) environment "(.*)"')
def test_case_foo_has_environment_bar(step, test_case, haveness, environment):
    # fetch the test case's resource identity
    test_case_id, version = get_testcase_resid(test_case)
    
    
#    if haveness.strip() == "does not have":

    world.conn.request("GET", add_params(world.path_testcases + test_case_id + "/environments"))
    response = world.conn.getresponse()
    verify_status(200, response, "Fetched environments")

    jsonList = get_resp_list(response, ns("environment"))

    found = False
    for item in jsonList:
        if (item.get(ns("name")) == environment):
            found = True
    
    shouldFind = (haveness == "has")
    eq_(found, shouldFind, "looking for environment of " + environment)


@step(u'test case with name "(.*)" (has|does not have) attachment with filename "(.*)"')
def test_case_foo_has_attachment_bar(step, test_case, haveness, attachment):
    # fetch the test case's resource identity
    test_case_id, version = get_testcase_resid(test_case)
    
    
#    if haveness.strip() == "does not have":

    world.conn.request("GET", add_params(world.path_testcases + test_case_id + "/attachments"))
    response = world.conn.getresponse()
    verify_status(200, response, "Fetched environments")

    jsonList = get_resp_list(response, "attachment")

    found = False
    for item in jsonList:
        if (item.get(ns("fileName")) == attachment):
            found = True
    
    shouldFind = (haveness == "has")
    eq_(found, shouldFind, "looking for attachment of " + attachment + " in:\n" + jstr(jsonList))

def get_stored_or_store_testcase_name(stored, name):
    '''
        Help figure out if the test writer wants to use a stored name from a previous step, or if
        the name was passed in explicitly. 
        
        If they refer to a user as 'that name' rather than 'name "foo bar"' then it uses
        the stored one.  Otherwise, the explicit name passed in.  
    '''
    if (stored.strip() == "that name"):
        name = world.testcase_name
    else:
        world.testcase_name = name
    return name
