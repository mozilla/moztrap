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

@step(u'And I create a new role with (that name|name "(.*)") with the following permissions')
def create_role_with_permissions(step, stored, name):
    name = get_stored_or_store_name("role", stored, name)
    
    # create the new role
    role_payload = {"companyId": get_seed_company_id(),
                    "name": name}
    do_post(world.path_roles, role_payload)
    
    #get the new role ID
    role_id, role_version = get_resource_identity("role", 
                                                  add_params(world.path_roles, 
                                                             {"name": name}))

    # get the list of all available permissions
    perm_array = get_list_from_search("permission", world.path_permissions)    
    
    # walk the hash of permissionCodes add these to the new role    
    for perm_code in step.hashes:
        permissionCode = perm_code["permissionCode"]
        
        # find the matching permission object based on the permissionCode field
        found_perm = [x for x in perm_array if x[ns("permissionCode")] == permissionCode] 
        assert found_perm != None, "Expected permissionCode: " + permissionCode
        assert len(found_perm) >= 1, "Should be at least one found"
        try:
            # there will always be only one that matches, in this case
            perm_id = found_perm[0][ns("resourceIdentity")]["@id"]
        except KeyError:
            assert False, "%s.%s not found in:\n%s" % (ns("resourceIdentity"), "@id", found_perm)
            
        # now add the permissions to that role
        perm_uri = world.path_roles + "%s/permissions/%s/" % (role_id, perm_id)
        perm_payload = {"permissionId": perm_id,
                        "originalVersionId": role_version}
        do_post(perm_uri, perm_payload)

@step(u'role with (that name|name "(.*)") has the following permissions')
def role_has_permissions(step, stored, role_name):
    role_name = get_stored_or_store_name("role", stored, role_name)

    role_id, role_version = get_resource_identity("role", 
                                                  add_params(world.path_roles, 
                                                             {"name": role_name}))

    perm_list = get_list_from_endpoint("permission",
                                       world.path_roles + role_id + "/permissions")
    
    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for perm_code in step.hashes:
        permissionCode = perm_code["permissionCode"]
        found_perm = [x for x in perm_list if x[ns("permissionCode")] == permissionCode] 
        
        assert len(found_perm) == 1, "Expected to find permissionCode %s in:\n%s" % (permissionCode,
                                                                                   str(perm_list))

      
@step(u'add the role with (that name|name "(.*)") to the user with (that name|name "(.*)")')
def add_role_to_user(step, stored_role, role_name, stored_user, user_name):
    user_name = get_stored_or_store_name("user", stored_user, user_name)
    role_name = get_stored_or_store_name("role", stored_role, role_name)
    
    # fetch the role's resource identity
    user_id, user_version = get_user_resid(user_name)
    role_id, role_version = get_resource_identity("role", 
                                                  add_params(world.path_roles, 
                                                             {"name": role_name}))
    
    do_post(world.path_users + "%s/roles/%s/" % (user_id, role_id), 
            {"originalVersionId": user_version})

@step(u'add the following roles to the user with (that name|name "(.*)")')
def add_roles_to_user(step, stored_role, role_name, stored_user, user_name):
    user_name = get_stored_or_store_name("user", stored_user, user_name)
    
    assert False, "need to implement adding all roles in the steps.hashes"
    
    
    role_name = get_stored_or_store_name("role", stored_role, role_name)
    
    # fetch the role's resource identity
    user_id, user_version = get_user_resid(user_name)
    role_id, role_version = get_resource_identity("role", 
                                                  add_params(world.path_roles, 
                                                             {"name": role_name}))
    do_put(world.path_users + "%s/roles/" % (user_id), 
            {"originalVersionId": user_version,
             "roleIds": role_id})
    


@step(u'user with (that name|name "(.*)") has the role with (that name|name "(.*)")')
def user_has_role(step, stored_user, user_name, stored_role, role_name):
    user_name = get_stored_or_store_name("user", stored_user, user_name)
    role_name = get_stored_or_store_name("role", stored_role, role_name)
    
    # fetch the role's resource identity
    user_id, user_version = get_user_resid(user_name)

    role_list = get_list_from_endpoint("role", 
                                       world.path_users + user_id + "/roles")

    found_role = [x for x in role_list if x[ns("name")] == role_name] 
    
    assert len(found_role) == 1, "Expected to find role with name %s in:\n%s" % (role_name,
                                                                               str(role_list))
    
    














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

@step(u'create a new role of "(.*)"')
def create_a_new_role_of_x(step, role):
    
    post_payload = {"description":role}

    do_post(world.path_roles, post_payload)
    

@step(u'add permission named "(.*)" to the role named "(.*)"')
def add_permission_foo_to_role_bar(step, permission, role):
    # this takes 2 requests.  
    #    1: get the id of this role
    #    2: add the permission to the role
    
    # fetch the role's resource identity
    role_id, version = get_role_resid(role)
    
    post_payload = {
                    "description": permission
                    }
    do_post(world.path_roles + role_id + "/permissions", 
            post_payload,
            params = {"originalVersionId": version})



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
            exp = exp_role.get("description")
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

