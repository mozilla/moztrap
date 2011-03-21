'''
Created on Jan 28, 2011

@author: camerondawson
'''
from features.models import UserModel, RoleModel, CompanyModel, PermissionModel
from features.tcm_data_helper import ns, jstr, list_size_check, \
    check_first_before_second, verify_single_item_in_list
from lettuce import step

'''
######################################################################

                     ROLE STEPS

######################################################################
'''

@step(u'create a new role with (that name|name "(.*)") with the following permissions')
def create_role_with_permissions(step, stored, name):
    roleModel = RoleModel()
    name = roleModel.get_stored_or_store_name(stored, name)

    # create the new role
    role_payload = {"companyId": CompanyModel().get_seed_resid()[0],
                    "name": name}
    roleModel.create(role_payload)

    #get the new role ID
    role_id, role_version = roleModel.get_resid(name)

    # get the list of all available permissions
    perm_array = PermissionModel().get_all_list()

    # walk the hash of permissionCodes add these to the new role
    for perm_code in step.hashes:
        permissionCode = perm_code["permissionCode"]

        # find the matching permission object based on the permissionCode field
        found_perm = verify_single_item_in_list(perm_array, "permissionCode", permissionCode)

        try:
            # there will always be only one that matches, in this case
            perm_id = found_perm[ns("resourceIdentity")]["@id"]
        except KeyError:
            assert False, "%s.%s not found in:\n%s" % (ns("resourceIdentity"), "@id", found_perm)

        # now add the permissions to that role
        roleModel.add_permission(role_id, role_version, perm_id)

@step(u'role with (that name|name "(.*)") has the following permissions')
def role_has_permissions(step, stored, role_name):
    roleModel = RoleModel()
    role_name = roleModel.get_stored_or_store_name(stored, role_name)

    perm_list = roleModel.get_permissions_list(role_name)

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
    userModel = UserModel()
    user_name = userModel.get_stored_or_store_name(stored_user, user_name)
    roleModel = RoleModel()
    role_name = roleModel.get_stored_or_store_name(stored_role, role_name)
    userModel.add_role(user_name, role_name)


@step(u'replace the role list for the user with (that name|name "(.*)") with these roles')
def replace_role_list_for_user(step, stored_user, user_name):
    userModel = UserModel()
    user_name = userModel.get_stored_or_store_name(stored_user, user_name)

    role_ids = []
    for role in step.hashes:
        role_id = RoleModel().get_resid(role["name"])[0]
        role_ids.append(role_id)


    userModel.set_roles(user_name, role_ids)

@step(u'remove the role with (that name|name "(.*)") from the user with (that name|name "(.*)")')
def remove_role_from_user(step, stored_role, role_name, stored_user, user_name):
    userModel = UserModel()
    user_name = userModel.get_stored_or_store_name(stored_user, user_name)
    roleModel = RoleModel()
    role_name = roleModel.get_stored_or_store_name(stored_role, role_name)

    userModel.remove_role(user_name, role_name)

@step(u'add the following roles to the user with (that name|name "(.*)")')
def add_roles_to_user(step, stored_user, user_name):
    userModel = UserModel()
    user_name = userModel.get_stored_or_store_name(stored_user, user_name)

    '''
        adds them one at a time in the model
    '''
    userModel.add_roles(user_name, step.hashes)


@step(u'user with (that name|name "(.*)") has the role with (that name|name "(.*)")')
def user_has_role(step, stored_user, user_name, stored_role, role_name):
    userModel = UserModel()
    user_name = userModel.get_stored_or_store_name(stored_user, user_name)
    roleModel = RoleModel()
    role_name = roleModel.get_stored_or_store_name(stored_role, role_name)

    userModel.has_role(user_name, role_name)

@step(u'at least this role exists:')
def at_least_this_role_exists(step):
    check_roles_exist(step.hashes)

@step(u'at least these roles exist:')
def at_least_these_roles_exist(step):
    check_roles_exist(step.hashes)

def check_roles_exist(hashes):
    roleModel = RoleModel()
    role_list = roleModel.get_all_list()

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
    roleModel = RoleModel()
    role_name = roleModel.get_stored_or_store_name(stored_role, role_name)

    role = roleModel.get_by_name(role_name)

    assert role[ns("name")] == role_name, "Expected to find role with name %s in:\n%s" % (role_name,
                                                                                 jstr(role))

@step(u'user with (that name|name "(.*)") has (at least|exactly) these roles')
def user_has_these_roles(step, stored_user, user_name, at_least_only):
    userModel = UserModel()
    user_name = userModel.get_stored_or_store_name(stored_user, user_name)

    role_list = userModel.get_role_list(user_name)

    list_size_check(at_least_only, step.hashes, role_list)

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
    roleModel = RoleModel()

    role_list = roleModel.get_all_list(sort_direction = order,
                                       sort_field = "name")

    # check that the index of "first" is before "second"
    check_first_before_second("name", first, second, role_list)


@step(u'user with (that name|name "(.*)") has (at least|exactly) these permissions')
def user_has_permissions(step, stored, user_name, at_least_only):
    userModel = UserModel()
    user_name = userModel.get_stored_or_store_name(stored, user_name)

    perm_list = userModel.get_permission_list(user_name)

    list_size_check(at_least_only, step.hashes, perm_list)

    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for perm_code in step.hashes:
        permissionCode = perm_code["permissionCode"]
        found_perm = [x for x in perm_list if x[ns("permissionCode")] == permissionCode]

        assert len(found_perm) == 1, "Expected to find permissionCode %s in:\n%s" % (permissionCode,
                                                                                   str(perm_list))


