'''
Created on Oct 7, 2010

@author: camerondawson
'''
from lettuce import *
#from numpy.ma.testutils import *
from step_helper import *
from step_helper import jstr, add_params, get_count
import httplib
import mock_scenario_data
import post_data

def setup_connection():
    world.conn = httplib.HTTPConnection(world.hostname, world.port) 


@before.each_step
def setup_step_connection(step):
    setup_connection() 

# DATA SETUP
# This is the function that uploads the expected data to the mock server.
#
# @todo Need to make this only run in DEBUG mode or something
@before.each_scenario
def setup_scenario_data(scenario):
    if (world.use_mock):
        scenarioData = mock_scenario_data.get_scenario_data(scenario.name).strip() 
    
        headers = {'content-Type':'text/plain',
                   "Content-Length": "%d" % len(scenarioData) }
    
        setup_connection()
        world.conn.request("POST", add_params(world.path_mockdata, {"scenario" : scenario.name}), "", headers)
    
        world.conn.send(scenarioData)
        world.conn.getresponse()

'''
######################################################################

                     USER STEPS

######################################################################
'''
  
@step(u'logged in as user "(.*)"')
def logged_in_as_user_foo(step, name):
    names = name.split()
    
    name_headers = { 'firstname':names[0], 'lastname': names[1] }

    world.conn.request("GET", add_params(world.path_users + "current"), None, name_headers)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")
    
    thisUser = get_single_item(response, ns("user"))

    #save this off for later steps
    world.userResId = thisUser.get("resourceIdentity").get("id")
    assert world.userResId != None, "must have some value for user resourceIdentity: "+ jstr(thisUser)
    
    assert_equal(thisUser.get(ns("firstname")), names[0], "First Name field didn't match")
    assert_equal(thisUser.get(ns("lastname")), names[1], "Last Name field didn't match")

    
@step(u'user "(.*)" is (.*)registered')
def user_foo_check_registration(step, name, registered):
    names = name.split()
    headers = {'Content-Type':'application/json',
               'Authorization': get_auth_header()}

    world.conn.request("GET", add_params(world.path_users, 
                                         {"firstName": names[0], "lastName": names[1]}), "", headers)
    response = world.conn.getresponse()

    assert_equal(response.status, 200, "registration status")

    
    if registered.strip() == "not":
        # expect an empty search result
        count = get_count(response, "user")
        assert_equal(count, 0, "result size zero")
    else:

        userJson = get_single_item(response, "user")
        assert_equal(userJson.get(ns("firstName")), names[0], "First Name field didn't match")
        assert_equal(userJson.get(ns("lastName")), names[1], "Last Name field didn't match")


@step(u'create new user named "(.*)"')
def submit_information_for_user_foo(step, name):
    names = name.split()
    
    xml_data = post_data.get_submit_user(names[0], names[1])
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(xml_data) }

    world.conn.request("POST", add_params(world.path_users), "", headers)
    world.conn.send(xml_data)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Create new user")


@step(u'user "(.*)" has active status "(.*)"')
def user_has_foo__has_active_status_bar(step, name, exp_active):
    names = name.split()
    world.conn.request("GET", add_params(world.path_users, 
                                         {"firstName": names[0], "lastName": names[1]}))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Fetched a user")

    userJson = get_single_item(response, "user")
    assert_equal(userJson.get("active"), exp_active, "active status")

# @TODO This function may not be useful.  Possibly dead code
@step(u'user "(.*)" has id of (\d+)')
def user_foo_has_id_of_bar(step, name, exp_id):
    act_id = get_user_resid(name)

    assert_equal(act_id, exp_id, "matching resourceIdentity")

@step(u'(activate|deactivate) user "(.*)"')
def activate_deactivate_user_foo(step, action, name):
    user_id = get_user_resid(name)
    
    world.conn.request("PUT", add_params(world.path_users + user_id + "/" + action))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, action +"ed user")

@step(u'user "(.*)" has these roles:')
def foo_has_these_roles(step, name):
    user_id = get_user_resid(name)

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
    user_id = get_user_resid(name)
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
    user_id = get_user_resid(name)
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
    user_id = get_user_resid(name)
    
    post_payload = post_data.get_submit_role(role)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_users + user_id + "/roles"), "", headers)
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
    role_id = get_role_resid(role)
    
    post_payload = post_data.get_submit_permission(permission)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_roles + role_id + "/permissions"), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "post new permission to role")



@step(u'role of "(.*)" has permission of "(.*)"')
def role_foo_has_permission_of_bar(step, role, permission):
    # This takes 2 requests to complete
    #    1: get the id of the role
    #    2: check that role has that permission
    
    # fetch the user's resource identity
    role_id = get_role_resid(role)

    world.conn.request("GET", add_params(world.path_roles + role_id + "/permissions"))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Fetched a permission")

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
    assert_equal(response.status, 200, "Fetched list of all roles")

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
    assert_equal(response.status, 200, "Fetched list of all roles")

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
    assert_equal(response.status, 200, "create new testcase")

@step(u'test case( with name)? "(.*)" (exists|does not exist)')
def test_case_exists_with_description_foo(step, ignore, name, existence):
    check_existence(step, world.path_testcases, "name", name, "testcase", existence)

@step(u'add environment "(.*)" to test case "(.*)"')
def add_environment_foo_to_test_case_bar(step, environment, test_case):
    # this takes 2 requests.  
    #    1: get the id of this test case
    #    2: add the environment to the test case
    
    # fetch the test case's resource identity
    test_case_id = get_test_case_resid(test_case)
    
    post_payload = post_data.get_submit_environment(environment)
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_testcases + test_case_id + "/environments"), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "post new environment to test_case")

@step(u'remove environment "(.*)" from test case "(.*)"')
def remove_environment_from_test_case(step, environment, test_case):
    # fetch the test case's resource identity
    test_case_id = get_test_case_resid(test_case)
    environment_id = get_environment_resid(environment)
    
    world.conn.request("DELETE", add_params(world.path_testcases + test_case_id + "/environments/" + environment_id))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "delete new environment from test case")

@step(u'test case "(.*)" (has|does not have) environment "(.*)"')
def test_case_foo_has_environment_bar(step, test_case, haveness, environment):
    # fetch the test case's resource identity
    test_case_id = get_test_case_resid(test_case)
    
    
#    if haveness.strip() == "does not have":

    world.conn.request("GET", add_params(world.path_testcases + test_case_id + "/environments"))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Fetched environments")

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
    test_case_id = get_test_case_resid(test_case)
    
    
#    if haveness.strip() == "does not have":

    world.conn.request("GET", add_params(world.path_testcases + test_case_id + "/attachments"))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Fetched environments")

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

@step(u'company "(.*)" (does not exist|exists)')
def check_company_foo_existence(step, company_name, existence):
    check_existence(step, world.path_companies, "name", company_name, "company", existence)


@step(u'add a new company with name "(.*)"')
def add_a_new_company_with_name_foo(step, company_name):
    post_payload = post_data.get_submit_company(company_name)
    headers = {'content-Type':'text/xml',
               "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_companies), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "create new testcase")

@step(u'search all Companies')
def search_all_companies(step):
    assert False, 'This step must be implemented'

'''
######################################################################

                     ENVIRONMENT STEPS

######################################################################
'''

@step(u'environment "(.*)" (does not exist|exists)')
def check_environment_foo_existence(step, environment_name, existence):
    check_existence(step, world.path_environments, "name", environment_name, "environment", existence)

@step(u'add a new environment with name "(.*)"')
def add_a_new_environment_with_name_foo(step, environment_name):
    post_payload = post_data.get_submit_environment(environment_name)
    headers = {'content-Type':'text/xml',
               "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_environments), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "create new environment")

'''
    @todo: we should make this DRY with the rest of the existence methods
'''
@step(u'environment type "(.*)" (does not exist|exists)')
def check_environment_type_foo_existence(step, env_type_name, existence):
    check_existence(step, world.path_environmenttypes, "name", env_type_name, "environmenttype", existence)


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
    assert_equal(response.status, 200, "create new environment type")

'''
######################################################################

                     PRODUCT STEPS

######################################################################
'''

@step(u'product "(.*)" (does not exist|exists)')
def check_product_foo_existence(step, product_name, existence):
    check_existence(step, world.path_products, "name", product_name, "product", existence)

@step(u'add environment "(.*)" to product "(.*)"')
def add_environment_foo_to_product_bar(step, environment, product):
    # this takes 2 requests.  
    #    1: get the id of this product
    #    2: add the environment to the product
    
    # fetch the product's resource identity
    product_id = get_product_resid(product)
    
    post_payload = post_data.get_submit_environment(environment)
    headers = {'content-Type':'text/xml',
               'Content-Length': "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_products + product_id + "/environments"), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "post new environment to product")

@step(u'remove environment "(.*)" from product "(.*)"')
def remove_environment_from_product(step, environment, product):
    # fetch the product's resource identity
    product_id = get_product_resid(product)
    environment_id = get_environment_resid(environment)
    
    world.conn.request("DELETE", add_params(world.path_products + product_id + "/environments/" + environment_id))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "delete new environment from product")

@step(u'product "(.*)" (has|does not have) environment "(.*)"')
def product_foo_has_environment_bar(step, product, haveness, environment):
    # fetch the product's resource identity
    product_id = get_product_resid(product)
    
    
#    if haveness.strip() == "does not have":

    world.conn.request("GET", add_params(world.path_products + product_id + "/environments"))
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Fetched environments")

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
    test_case_id = get_test_case_resid(test_case)

    content_type, body = encode_multipart_formdata([], [{'key': attachment, 
                                                         'filename': attachment, 
                                                         'value': open(world.testfile_dir + attachment, 'rb')}])

    headers = {"Accept": "application/xml", 
               "Content-Type":content_type,
               "Content-Length": "%d" % len(body) }

    world.conn.request("POST", add_params(world.path_testcases + test_case_id + "/attachments/upload"), body, headers)

    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Create new user")
    








