'''
Created on Jan 28, 2011

@author: camerondawson
'''
from lettuce import *
#from nose.tools import *
from step_helper import *

'''
######################################################################

                     USER HELPER FUNCTIONS

######################################################################
'''

def create_user_from_obj(user_obj):
    '''
        Create a user based on an already formed user object
    '''
    do_post(world.path_users,
            user_obj)
    
def create_user_from_name(name):
    '''
        Create a user based on just the user name and seed data
    '''
    names = name.split()
    fname = names[0]
    lname = names[1]
    user_obj = {
                "firstName":fname,
                "lastName":lname,
                "email":fname+lname + "@mozilla.com",
                "screenName":fname+lname,
                "password":get_user_password(name),
                "companyId":get_seed_company_id(),
    } 
    create_user_from_obj(user_obj)

'''
######################################################################

                     USER STEPS

######################################################################
'''
    

@step(u'create a new user with (that name|name "(.*)")')
def create_user_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    create_user_from_name(name)
    
@step(u'logged in as user "(.*)"')
def logged_in_as_user_foo(step, name):
    names = name.split()
    world.user_name = name
    
    params = { 'firstName':names[0], 'lastName': names[1] }
    data = do_get(world.path_users + "current", params)
    
    thisUser = get_single_item(data, ns("user"))

    eq_(thisUser.get(ns("firstName")), names[0], "First Name field didn't match")
    eq_(thisUser.get(ns("lastName")), names[1], "Last Name field didn't match")

@step(u'user with (that name|name "(.*)") (exists|does not exist)')
def check_user_foo_existence(step, stored, name, existence):
    names = get_stored_or_store_name("user", stored, name).split()
    search_and_verify_existence(world.path_users, 
                    {"firstName": names[0], "lastName": names[1]}, 
                    "user", existence)

@step(u'user with (that name|name "(.*)") is (active|inactive|disabled)')
def check_user_foo_activated(step, stored, name, userStatus):
    names = get_stored_or_store_name("user", stored, name).split()
    statusId = get_user_status_id(userStatus) 
        
    # we DO expect to find this user, but we're just checking if they're activated or 
    # deactivated
    search_and_verify(world.path_users, 
                    {"firstName": names[0], "lastName": names[1], "userStatusId": statusId}, 
                    "user", True)
    
@step(u'(activate|deactivate) the user with (that name|name "(.*)")')
def activate_user_with_name_foo(step, status_action, stored, name):
    '''
        Users are not deleted, they're just registered or unregistered.
    '''
    name = get_stored_or_store_name("user", stored, name)
    resid, version = get_user_resid(name)

    do_put(world.path_users_activation % (resid, status_action), {"originalVersionId": version})


@step(u'user with (that name| name "(.*)") has at least these assignments:')
def foo_has_these_assignments(step, stored_user, user_name):
    user_name = get_stored_or_store_name("user", stored_user, user_name)
    
    user_id = get_user_resid(user_name)[0]
    assignment_list = get_list_from_endpoint("assignments",
                                     world.path_users + user_id + "/assignments")
    
    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for role in step.hashes:
        role_name = role["name"]
        found_perm = [x for x in assignment_list if x[ns("name")] == role_name] 
        
        assert len(found_perm) == 1, "Expected to find assignment name %s in:\n%s" % (role_name,
                                                                                jstr(assignment_list))

    
