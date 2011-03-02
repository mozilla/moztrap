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

@step(u'create a new role with (that name|name "(.*)") with the following permissions')
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

    role_id = get_role_resid(role_name)[0]

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
    role_id = get_role_resid(role_name)[0]
    
    do_post(world.path_users + "%s/roles/%s/" % (user_id, role_id), 
            {"originalVersionId": user_version})

@step(u'add the following roles to the user with (that name|name "(.*)")')
def add_roles_to_user(step, stored_user, user_name):
    user_name = get_stored_or_store_name("user", stored_user, user_name)
    
    # fetch the role's resource identity
    user_id, user_version = get_user_resid(user_name)

    role_ids = []
    for role in step.hashes:
        role_id = get_role_resid(role["name"])[0]
        role_ids.append(role_id)

    do_put(world.path_users + "%s/roles/" % (user_id), 
            {"originalVersionId": user_version,
             "roleIds": role_ids})
    


@step(u'user with (that name|name "(.*)") has the role with (that name|name "(.*)")')
def user_has_role(step, stored_user, user_name, stored_role, role_name):
    user_name = get_stored_or_store_name("user", stored_user, user_name)
    role_name = get_stored_or_store_name("role", stored_role, role_name)
    
    # fetch the role's resource identity
    user_id = get_user_resid(user_name)[0]

    role_list = get_list_from_endpoint("role", 
                                       world.path_users + user_id + "/roles")

    found_role = [x for x in role_list if x[ns("name")] == role_name] 
    
    assert len(found_role) == 1, "Expected to find role with name %s in:\n%s" % (role_name,
                                                                               str(role_list))

@step(u'at least this role exists:')
def at_least_this_role_exists(step):
    check_roles_exist(step.hashes)
    
@step(u'at least these roles exist:')
def at_least_these_roles_exist(step):
    check_roles_exist(step.hashes)
    
def check_roles_exist(hashes):
    role_list = get_list_from_search("role",
                                     world.path_roles)
    
    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for role in hashes:
        role_name = role["name"]
        found_perm = [x for x in role_list if x[ns("name")] == role_name] 
        
        assert len(found_perm) == 1, "Expected to find role name %s in:\n%s" % (role_name,
                                                                                   jstr(role_list))

@step(u'find the role with (that name|name "(.*)") by id')
def find_role_by_id(step, stored_role, role_name):
    role_name = get_stored_or_store_name("role", stored_role, role_name)

    # fetch the role's resource identity
    role_id = get_role_resid(role_name)[0]

    role = get_single_item_from_endpoint("role",  
                                       world.path_roles + role_id)

    assert role[ns("name")] == role_name, "Expected to find role with name %s in:\n%s" % (role_name,
                                                                                 jstr(role))
    
@step(u'user with (that name|name "(.*)") has at least these roles')
def user_has_at_least_these_roles(step, stored_user, user_name):
    user_name = get_stored_or_store_name("user", stored_user, user_name)
    
    user_id = get_user_resid(user_name)[0]
    role_list = get_list_from_endpoint("role",
                                     world.path_users + user_id + "/roles/")
    
    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for role in step.hashes:
        role_name = role["name"]
        found_perm = [x for x in role_list if x[ns("name")] == role_name] 
        
        assert len(found_perm) == 1, "Expected to find role name %s in:\n%s" % (role_name,
                                                                                jstr(role_list))
    

@step(u'"(ASC|DESC)" role searches list "(.*)" before "(.*)"')
def order_role_searches_list_foo_before_bar(step, order, first, second):
    
    role_list = get_list_from_search("role",
                                     world.path_roles, 
                                     {"sortDirection": order, "sortField": "name"}
                                    )

    # check that the index of "first" is before "second"
    check_first_before_second("name", first, second, role_list) 
    









'''
######################################################################

                     NEED REFACTORING

######################################################################
'''


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




