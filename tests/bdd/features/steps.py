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

                     USER STEPS

######################################################################
'''
def get_stored_or_store_user_name(stored, name):
    '''
        Help figure out if the test writer wants to use a stored name from a previous step, or if
        the name was passed in explicitly. 
        
        If they refer to a user as 'that name' rather than 'name "foo bar"' then it uses
        the stored one.  Otherwise, the explicit name passed in.  
    '''
    if (stored.strip() == "that name"):
        name = world.user_name
    else:
        world.user_name = name
    return name
  
@step(u'logged in as user "(.*)"')
def logged_in_as_user_foo(step, name):
    names = name.split()
    world.user_name = name
    
    name_headers = { 'firstname':names[0], 'lastname': names[1] }

    world.conn.request("GET", add_params(world.path_users + "current"), None, name_headers)
    response = world.conn.getresponse()
    data = verify_status(200, response, "Fetched a user")
    
    thisUser = get_single_item(data, ns("user"))

    assert_equal(thisUser.get(ns("firstname")), names[0], "First Name field didn't match")
    assert_equal(thisUser.get(ns("lastname")), names[1], "Last Name field didn't match")

@step(u'user with (that name|name "(.*)") (exists|does not exist)')
def check_user_foo_existence(step, stored, name, existence):
    names = get_stored_or_store_user_name(stored, name).split()
    search_and_verify_existence(step, world.path_users, 
                    {"firstName": names[0], "lastName": names[1]}, 
                    "user", existence)

@step(u'user with (that name|name "(.*)") is (active|inactive|disabled)')
def check_user_foo_activated(step, stored, name, userStatus):
    names = get_stored_or_store_user_name(stored, name).split()
    statusId = get_user_status_id(userStatus) 
        
    # we DO expect to find this user, but we're just checking if they're activated or 
    # deactivated
    search_and_verify(step, world.path_users, 
                    {"firstName": names[0], "lastName": names[1], "userStatusId": statusId}, 
                    "user", True)
    
@step(u'create a new user with (that name|name "(.*)")')
def create_user_with_name_foo(step, stored, name):
    names = get_stored_or_store_user_name(stored, name).split()
    
    post_payload = post_data.get_submit_user_params(names[0], names[1])
    headers = {'Authorization': get_auth_header()}

    world.conn.request("POST", add_params(world.path_users, post_payload), "", headers)

    response = world.conn.getresponse()
    verify_status(200, response, "Create new user")

@step(u'(activate|deactivate) the user with (that name|name "(.*)")')
def activate_user_with_name_foo(step, status_action, stored, name):
    '''
        Users are not deleted, they're just registered or unregistered.
    '''
    name = get_stored_or_store_user_name(stored, name)
    
    resid, version = get_user_resid(name)
    headers = {'Authorization': get_auth_header()}

    url = add_params(world.path_users_activation % (resid, status_action), {"originalVersionId": version})
    world.conn.request("PUT", url, "", headers)

    response = world.conn.getresponse()
    verify_status(200, response, "%s new user" % (status_action))

@step(u'user "(.*)" has active status "(.*)"')
def user_has_foo__has_active_status_bar(step, name, exp_active):
    names = name.split()
    
    world.conn.request("GET", add_params(world.path_users, 
                                         {"firstName": names[0], "lastName": names[1]}))
    response = world.conn.getresponse()
    data = verify_status(200, response, "Fetched a user")

    userJson = get_single_item(data, "user")
    assert_equal(userJson.get("active"), exp_active, "active status")

@step(u'user "(.*)" has these roles:')
def foo_has_these_roles(step, name):
    user_id, version = get_user_resid(name)

    world.conn.request("GET", add_params(world.path_users + user_id + "/roles"))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    # walk through all roles for this user to see if it has the requested one
    respJson = get_resp_list(response, "role")

    # now walk through the expected roles and check the response
    # to see that it is represented
    roles = step.hashes
    for exp_role in roles:
        found = False
        for act_role in respJson:
            exp = exp_role.get(ns("description"))
            act = act_role.get(ns("description"))
            if (exp == act):
                found = True
        assert_equal(found, True, "expected role of: " + exp)

@step(u'user "(.*)" has these assignments:')
def foo_has_these_assignments(step, name):
    user_id, version = get_user_resid(name)
    world.conn.request("GET", add_params(world.path_users + user_id + "/assignments"))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    # walk through all roles for this user to see if it has the requested one
    respJson = get_resp_list(response, "testcase")

    # now walk through the expected roles and check the response
    # to see that it is represented
    exp_list = step.hashes
    for exp_item in exp_list:
        found = False
        for act_item in respJson:
            exp = exp_item.get(ns("name"))
            act = act_item.get(ns("name"))
            if (exp == act):
                found = True
        assert_equal(found, True, "expected assignment of: " + str(exp) +
                      "\nin response:\n" + jstr(respJson))


'''
######################################################################

                     ROLE STEPS

######################################################################
'''


@step(u'I have the role of "(.*)"')
def i_have_the_role_of_bar(step, role):
    assert world.userResId != None, "must have some value for user resourceIdentity"
    user_id_role_check(world.userResId, role, True, "should have role of " + role)


@step(u'user "(.*)" has the role of "(.*)"')
def user_foo_has_the_role_of_bar(step, name, role):
    user_role_check(name, role, True, "should have role of " + role)

@step(u'user "(.*)" does not already have the role of "(.*)"')
def foo_does_not_already_have_the_role_of_bar(step, name, role):
    user_role_check(name, role, False, "should not have role of " + role)

def user_role_check(name, role, expected_tf, assert_text):
    
    # fetch the user's resource identity
    user_id, version = get_user_resid(name)
    return user_id_role_check(user_id, role, expected_tf, assert_text)

def user_id_role_check(user_id, role, expected_tf, assert_text):
    # This takes 2 requests to complete
    #    1: get the id of the user
    #    2: check that user has that role
    
    world.conn.request("GET", add_params(world.path_users + str(user_id) + "/roles"))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    # walk through all roles for this user to see if it has the requested one
    
    roleJsonList = get_resp_list(response, ns("role")) 
    
    foundRole = False
    for roleJson in roleJsonList:
        assert isinstance(roleJson, dict), "unexpected type:\n" + jstr(roleJson)
        if (roleJson.get(ns("description")) == role):
            foundRole = True
    assert_equal(foundRole, expected_tf, assert_text + ": " + jstr(roleJsonList))

@step(u'add role of "(.*)" to user "(.*)"')
def add_role_of_foo_to_user_bar(step, role, name):
    '''
    # this takes 2 requests.  
    #    1: get the id of this user
    #    2: add the role to the user
    '''
    
    # fetch the role's resource identity
    user_id, version = get_user_resid(name)
    
    post_payload = post_data.get_submit_role(role)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_users + user_id + "/roles", {"originalVersionId": version}), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "post new role to user")

@step(u'create a new role of "(.*)"')
def create_a_new_role_of_x(step, new_role):
    
    json_data = post_data.get_submit_role(new_role)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(json_data) }

    world.conn.request("POST", add_params(world.path_roles), "", headers)
    world.conn.send(json_data)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Create new role")
    

@step(u'add permission of "(.*)" to the role of "(.*)"')
def add_permission_foo_to_role_bar(step, permission, role):
    # this takes 2 requests.  
    #    1: get the id of this role
    #    2: add the permission to the role
    
    # fetch the role's resource identity
    role_id, version = get_role_resid(role)
    
    post_payload = post_data.get_submit_permission(permission)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_roles + role_id + "/permissions", {"originalVersionId": version}), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "post new permission to role")



@step(u'role of "(.*)" has permission of "(.*)"')
def role_foo_has_permission_of_bar(step, role, permission):
    # This takes 2 requests to complete
    #    1: get the id of the role
    #    2: check that role has that permission
    
    # fetch the user's resource identity
    role_id, version = get_role_resid(role)

    world.conn.request("GET", add_params(world.path_roles + role_id + "/permissions"))
    response = world.conn.getresponse()
    verify_status(200, response, "Fetched a permission")

    permJsonList = get_resp_list(response, "permission")
    # walk through all roles for this user to see if it has the requested one
    for item in permJsonList:
        found = False
        if (item.get(ns("description")) == permission):
            found = True
    assert_equal(found, True, "looking for permission of " + permission)

@step(u'role of "(.*)" exists')
def role_of_foo_exists(step, role):
    check_role_existence([{"description": role}])
    

@step(u'at least these roles exist:')
def at_least_these_roles_exist(step):
    check_role_existence(step.hashes)
    
def check_role_existence(roles):
    
    # fetch the user's resource identity
    world.conn.request("GET", add_params(world.path_roles))
    response = world.conn.getresponse()
    verify_status(200, response, "Fetched list of all roles")

    respJson = get_resp_list(response, "role")

    # now walk through the expected roles and check the response
    # to see that it is represented
    for exp_role in roles:
        found = False
        for act_role in respJson:
            exp = exp_role.get(ns("description"))
            act = act_role.get(ns("description"))
            if (exp == act):
                found = True
        assert_equal(found, True, "Didn't find role of:\n" + jstr(exp_role) + 
                     "\n in data:\n" + jstr(respJson))


@step(u'"(ASC|DESC)" role searches list "(.*)" before "(.*)"')
def order_role_searches_list_foo_before_bar(step, order, first, second):
    
    # fetch the user's resource identity
    world.conn.request("GET", add_params(world.path_roles, {"sortDirection": order}))
    response = world.conn.getresponse()
    verify_status(200, response, "Fetched list of all roles")

    respJson = get_resp_list(response, "role")

    find_ordered_response("role", "description", first, second, respJson)

'''
######################################################################

                     TEST CASE STEPS

######################################################################
'''

@step(u'submit a new test case with name "(.*)"')
def submit_a_new_test_case_with_description_foo(step, name):
    post_payload = post_data.get_submit_test_case(name)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_testcases), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    verify_status(200, response, "create new testcase")

@step(u'test case( with name)? "(.*)" (exists|does not exist)')
def test_case_exists_with_description_foo(step, ignore, name, existence):
    search_and_verify_existence(step, world.path_testcases, {"name": name}, "testcase", existence)

@step(u'add environment "(.*)" to test case "(.*)"')
def add_environment_foo_to_test_case_bar(step, environment, test_case):
    # this takes 2 requests.  
    #    1: get the id of this test case
    #    2: add the environment to the test case
    
    # fetch the test case's resource identity
    test_case_id, version = get_test_case_resid(test_case)
    
    post_payload = post_data.get_submit_environment(environment)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", 
                       add_params(world.path_testcases + test_case_id + "/environments", 
                                  {"orifinalVersionId": version}), 
                       "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    verify_status(200, response, "post new environment to test_case")

@step(u'remove environment "(.*)" from test case "(.*)"')
def remove_environment_from_test_case(step, environment, test_case):
    # fetch the test case's resource identity
    test_case_id, version = get_test_case_resid(test_case)
    environment_id = get_environment_resid(environment)
    
    world.conn.request("DELETE", 
                       add_params(world.path_testcases + test_case_id + "/environments/" + environment_id, 
                                  {"originalVersionId": version}))
    response = world.conn.getresponse()
    verify_status(200, response, "delete new environment from test case")

@step(u'test case "(.*)" (has|does not have) environment "(.*)"')
def test_case_foo_has_environment_bar(step, test_case, haveness, environment):
    # fetch the test case's resource identity
    test_case_id, version = get_test_case_resid(test_case)
    
    
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
    assert_equal(found, shouldFind, "looking for environment of " + environment)


@step(u'test case with name "(.*)" (has|does not have) attachment with filename "(.*)"')
def test_case_foo_has_attachment_bar(step, test_case, haveness, attachment):
    # fetch the test case's resource identity
    test_case_id, version = get_test_case_resid(test_case)
    
    
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
    assert_equal(found, shouldFind, "looking for attachment of " + attachment + " in:\n" + jstr(jsonList))

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

                     ENVIRONMENT STEPS

######################################################################
'''

@step(u'environment with name "(.*)" (does not exist|exists)')
def check_environment_foo_existence(step, environment_name, existence):
    search_and_verify_existence(step, world.path_environments, {"name": environment_name}, "environment", existence)

@step(u'add a new environment with name "(.*)"')
def add_a_new_environment_with_name_foo(step, environment_name):
    post_payload = post_data.get_submit_environment(environment_name)
    headers = {'content-Type':'text/xml',
               "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_environments), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    verify_status(200, response, "create new environment")

'''
    @todo: we should make this DRY with the rest of the existence methods
'''
@step(u'environment type with name "(.*)" (does not exist|exists)')
def check_environment_type_foo_existence(step, env_type_name, existence):
    search_and_verify_existence(step, world.path_environmenttypes, {"name": env_type_name}, "environmenttype", existence)


'''
    @todo: we should make this DRY with the rest of the existence methods
'''
@step(u'add a new environment type with name "(.*)"')
def add_a_new_environment_type_with_name_foo(step, env_type_name):
    post_payload = post_data.get_submit_environment(env_type_name)
    headers = {'content-Type':'text/xml',
               "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_environmenttypes), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    verify_status(200, response, "create new environment type")

'''
######################################################################

                     PRODUCT STEPS

######################################################################
'''

@step(u'product with name "(.*)" (does not exist|exists)')
def check_product_foo_existence(step, product_name, existence):
    search_and_verify_existence(step, world.path_products, {"name": product_name}, "product", existence)

@step(u'add environment "(.*)" to product "(.*)"')
def add_environment_foo_to_product_bar(step, environment, product):
    # this takes 2 requests.  
    #    1: get the id of this product
    #    2: add the environment to the product
    
    # fetch the product's resource identity
    product_id, version = get_product_resid(product)
    
    post_payload = post_data.get_submit_environment(environment)
    headers = {'content-Type':'text/xml',
               'Content-Length': "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_products + product_id + "/environments", {"originalVersionId": version}), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    verify_status(200, response, "post new environment to product")

@step(u'remove environment "(.*)" from product "(.*)"')
def remove_environment_from_product(step, environment, product):
    # fetch the product's resource identity
    product_id, version = get_product_resid(product)
    environment_id = get_environment_resid(environment)
    
    world.conn.request("DELETE", 
                       add_params(world.path_products + product_id + "/environments/" + environment_id, 
                                  {"originalVersionId": version}))
    response = world.conn.getresponse()
    verify_status(200, response, "delete new environment from product")

@step(u'product "(.*)" (has|does not have) environment "(.*)"')
def product_foo_has_environment_bar(step, product, haveness, environment):
    # fetch the product's resource identity
    product_id, version = get_product_resid(product)
    
    
#    if haveness.strip() == "does not have":

    world.conn.request("GET", add_params(world.path_products + product_id + "/environments"))
    response = world.conn.getresponse()
    verify_status(200, response, "Fetched environments")

    jsonList = get_resp_list(response, "environment")

    found = False
    for item in jsonList:
        assert isinstance(item, dict), "expected a list of dicts in:\n" + jstr(jsonList)
        if (item.get(ns("name")) == environment):
            found = True
    
    shouldFind = (haveness == "has")
    assert_equal(found, shouldFind, "looking for environment of " + environment)

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
    








