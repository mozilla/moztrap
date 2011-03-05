'''
Created on Jan 28, 2011

@author: camerondawson
'''
from features.step_helper import get_stored_or_store_name, get_seed_company_id, \
    do_post, ns, get_list_from_endpoint, get_user_resid, do_put, jstr, \
    get_user_password, do_get, get_single_item, eq_, search_and_verify_existence, \
    get_user_status_id, search_and_verify, get_company_resid, get_list_from_search, \
    log_user_in, get_auth_header, get_json_headers, do_put_for_cookie, \
    get_single_item_from_endpoint
from lettuce import step, world

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
    
@step(u'update the user with (that name|name "(.*)") to have these values')
def update_user_with_name(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    
    
    user_id, version = get_user_resid(name)

    new_values = step.hashes[0].copy()
    company_id = get_company_resid(new_values["company name"])
    new_values["companyId"] = company_id
    del new_values["company name"]
    new_values["originalVersionId"] = version

    do_put(world.path_users + user_id, new_values)

@step(u'user with (that name|name "(.*)") has these values')
def user_with_name_has_values(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    names = name.split()
    
    act_user = get_list_from_search("user", world.path_users, 
                                {"firstName": names[0], "lastName": names[1]})[0]

    exp_user = step.hashes[0].copy()
    exp_user["companyId"] = get_company_resid(exp_user["company name"])[0]
    
    # check that the data matches
    eq_(act_user.get(ns("firstName")), exp_user["firstName"], "First Name field didn't match")
    eq_(act_user.get(ns("lastName")), exp_user["lastName"], "lastName field didn't match")
    eq_(act_user.get(ns("email")), exp_user["email"], "email field didn't match")
    eq_(act_user.get(ns("screenName")), exp_user["screenName"], "screenName field didn't match")
    eq_(act_user.get(ns("companyId")), int(exp_user["companyId"]), "companyId field didn't match")
    

@step(u'change the email to "(.*)" for the user with (that name|name "(.*)")')
def change_user_email(step, new_email, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    user_id, version = get_user_resid(name)

    do_put(world.path_users + user_id + "/emailchange/%s" % new_email,
           {"originalVersionId": version})    

@step(u'change the password to "(.*)" for the user with (that name|name "(.*)")')
def change_user_password(step, new_pw, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    user_id, version = get_user_resid(name)

    do_put(world.path_users + user_id + "/passwordchange/%s" % new_pw,
           {"originalVersionId": version})    


@step(u'log out the user with (that name|name "(.*)")')
def log_out(step, stored, user_name):
    user_name = get_stored_or_store_name("user", stored, user_name)

    headers = {'cookie': world.auth_cookie,
               'Content-Type':'application/json' }

    return do_put(world.path_users + "logout", "", headers)
    
    
@step(u'log in user with (that name|name "(.*)")')
def log_in_with_name(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)

    cookie = log_user_in(name)[1]
    # store the cookie in world
    world.auth_cookie = cookie

@step(u'log in user with these credentials')
def log_in_with_credentials(step):
    user = step.hashes[0]
    headers = get_json_headers(get_auth_header(user["email"], user["password"]))
    
    cookie = do_put_for_cookie(world.path_users + "login", "", headers)[1]
    world.auth_cookie = cookie
    # store the cookie in world

@step(u'logged in as the user with (that name|name "(.*)")')
def logged_in_as_user(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    names = name.split()
    
    headers = {'cookie': world.auth_cookie,
               'Content-Type':'application/json' }
    
    thisUser = get_single_item_from_endpoint("user", 
                                             world.path_users + "current", 
                                             headers = headers)
    
    eq_(thisUser[ns("firstName")], names[0], "First Name field didn't match")
    eq_(thisUser[ns("lastName")], names[1], "Last Name field didn't match")

@step(u'that user is not logged in')
def user_not_logged_in(step):
    headers = {'cookie': world.auth_cookie,
               'Content-Type':'application/json' }
    
    thisUser = get_single_item_from_endpoint("user", 
                                             world.path_users + "current", 
                                             headers = headers)
    assert False, thisUser
    

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

    
