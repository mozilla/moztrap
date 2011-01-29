'''
Created on Jan 28, 2011

@author: camerondawson
'''
from lettuce import *
from step_helper import *

'''
######################################################################

                     ENVIRONMENT STEPS

######################################################################
'''

@step(u'environment with (that name|name "(.*)") (exists|does not exist)')
def check_user_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_environment_name(stored, name)
    search_and_verify_existence(step, world.path_testcases, 
                    {"name": name}, 
                    "environment", existence)

@step(u'create a new environment with (that name|name "(.*)")')
def create_testcase_with_name_foo(step, stored, name):
    name = get_stored_or_store_environment_name(stored, name)
    
    headers = {'Authorization': get_auth_header(),
               'content-type': "application/x-www-form-urlencoded"
               }
               
    post_payload = {
                    "name": name,
                    "localeCode": "en_US",
                    "sortOrder": "0",
                    "environmentTypeId": "1",
                    "resourceIdentity": "...",
                    "timeline": "..."
            }
    
    world.conn.request("POST", add_params(world.path_environments), 
                       urllib.urlencode(post_payload, doseq=True), 
                       headers)

    response = world.conn.getresponse()
    verify_status(200, response, "Create new environemtn")

'''
    @todo: we should make this DRY with the rest of the existence methods
'''
@step(u'environment type with name "(.*)" (does not exist|exists)')
def check_environment_type_foo_existence(step, env_type_name, existence):
    search_and_verify_existence(step, world.path_environmenttypes, {"name": env_type_name}, "environmenttype", existence)


def get_stored_or_store_environment_name(stored, name):
    '''
        Help figure out if the test writer wants to use a stored name from a previous step, or if
        the name was passed in explicitly. 
        
        If they refer to a user as 'that name' rather than 'name "foo bar"' then it uses
        the stored one.  Otherwise, the explicit name passed in.  
    '''
    if (stored.strip() == "that name"):
        name = world.environment_name
    else:
        world.environment_name = name
    return name
