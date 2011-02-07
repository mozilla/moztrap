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
    eq_(response.status, 200, "Fetched a user")

    # walk through all roles for this user to see if it has the requested one
    
    roleJsonList = get_resp_list(response, ns("role")) 
     
    foundRole = False
    for roleJson in roleJsonList:
        assert isinstance(roleJson, dict), "unexpected type:\n" + jstr(roleJson)
        if (roleJson.get(ns("description")) == role):
            foundRole = True
    eq_(foundRole, expected_tf, assert_text + ": " + jstr(roleJsonList))

@step(u'add role of "(.*)" to user "(.*)"')
def add_role_of_foo_to_user_bar(step, role, name):
    '''
    # this takes 2 requests.  
    #    1: get the id of this user
    #    2: add the role to the user
    '''
    
    # fetch the role's resource identity
    user_id, version = get_user_resid(name)
    
    post_payload = {
                    "description":role
                    }
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_users + user_id + "/roles", {"originalVersionId": version}), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    eq_(response.status, 200, "post new role to user")

@step(u'create a new role of "(.*)"')
def create_a_new_role_of_x(step, role):
    
    post_payload = {
                    "description":role
                    }
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_roles), post_payload, headers)
    response = world.conn.getresponse()
    eq_(response.status, 200, "Create new role")
    

@step(u'add permission of "(.*)" to the role of "(.*)"')
def add_permission_foo_to_role_bar(step, permission, role):
    # this takes 2 requests.  
    #    1: get the id of this role
    #    2: add the permission to the role
    
    # fetch the role's resource identity
    role_id, version = get_role_resid(role)
    
    post_payload = {
                    "description": permission
                    }
    headers = { 'content-Type':'text/xml',
            "Content-Length": "%d" % len(post_payload) }

    world.conn.request("POST", add_params(world.path_roles + role_id + "/permissions", {"originalVersionId": version}), "", headers)
    world.conn.send(post_payload)
    response = world.conn.getresponse()
    eq_(response.status, 200, "post new permission to role")



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
    eq_(found, True, "looking for permission of " + permission)

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
        eq_(found, True, "Didn't find role of:\n" + jstr(exp_role) + 
                     "\n in data:\n" + jstr(respJson))


@step(u'"(ASC|DESC)" role searches list "(.*)" before "(.*)"')
def order_role_searches_list_foo_before_bar(step, order, first, second):
    
    # fetch the user's resource identity
    world.conn.request("GET", add_params(world.path_roles, {"sortDirection": order}))
    response = world.conn.getresponse()
    verify_status(200, response, "Fetched list of all roles")

    respJson = get_resp_list(response, "role")

    find_ordered_response("role", "description", first, second, respJson)

