'''
Created on Jan 28, 2011

@author: camerondawson
'''
from features.tcm_data_helper import compare_dicts_by_keys, ns_keys, \
    get_stored_or_store_name, get_user_status_id
from features.tcm_request_helper import get_seed_company_id, do_post, ns, \
    get_list_from_endpoint, get_user_resid, do_put, jstr, get_user_password, do_get, \
    eq_, search_and_verify_existence, search_and_verify, get_company_resid, \
    log_user_in, get_auth_header, get_json_headers, do_put_for_cookie, \
    get_single_item_from_endpoint, json_to_obj, get_single_item_from_search, \
    get_resource_identity, store_latest_of_type, get_latest_of_type
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
    data = do_post(world.path_users,
            user_obj)
#    assert False, data
    created_obj = json_to_obj(data)[ns("user")][0]
    compare_dicts_by_keys(ns_keys(user_obj),
                          created_obj,
                          ("firstName", "lastName", "email", "screenName", "companyId"))

    # last referenced object of that type.  Then I can fetch whatever I want from it.  Though
    # the originalVersionId can be out of date.
    store_latest_of_type("user", created_obj)

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

@step(u'get that newly created user by id')
def get_new_user_by_id(step):
    last_created_user = get_latest_of_type("user")
    id = last_created_user[ns("resourceIdentity")]["@id"]
    data = do_get(world.path_users + str(id))

    compare_dicts_by_keys(last_created_user,
                          json_to_obj(data)[ns("user")][0],
                          ("firstName", "lastName", "email", "screenName", "companyId"))

@step(u'update the user with (that name|name "(.*)") to have these values')
def update_user_with_name(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)


    user_id, version = get_user_resid(name)

    new_values = step.hashes[0].copy()
    company_id = get_company_resid(new_values["company name"])
    new_values["companyId"] = company_id
    del new_values["company name"]
    new_values["originalVersionId"] = version

    do_put(world.path_users + str(user_id), new_values)

@step(u'user with (that name|name "(.*)") has these values')
def user_with_name_has_values(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    names = name.split()

    act_user = get_single_item_from_search("user", world.path_users,
                                    {"firstName": names[0], "lastName": names[1]})

    exp_user = step.hashes[0].copy()
    try:
        exp_user["companyId"] = get_company_resid(exp_user["company name"])[0]
        del exp_user["company name"]
    except KeyError:
        # we may not be checking company name, and that's ok, so just pass
        pass

    # check that the data matches
    compare_dicts_by_keys(ns_keys(exp_user),
                          act_user,
                          exp_user.keys())

@step(u'that user has these values')
def last_referenced_user_has_values(step):
    user_id = get_resource_identity(get_latest_of_type("user"))[0]

    act_user = get_single_item_from_endpoint("user", world.path_users + str(user_id))

    exp_user = step.hashes[0].copy()
    try:
        exp_user["companyId"] = get_company_resid(exp_user["company name"])[0]
        del exp_user["company name"]
    except KeyError:
        # we may not be checking company name, and that's ok, so just pass
        pass

    # check that the data matches
    compare_dicts_by_keys(ns_keys(exp_user),
                          act_user,
                          exp_user.keys())

@step(u'change the email to "(.*)" for the user with (that name|name "(.*)")')
def change_user_email(step, new_email, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    user_id, version = get_user_resid(name)

    do_put(world.path_users + "%s/emailchange/%s" % (user_id, new_email),
           {"originalVersionId": version})

@step(u'confirm the email for the user with (that name|name "(.*)")')
def confirm_user_email(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    user_id, version = get_user_resid(name)

    do_put(world.path_users + "%s/emailconfirm" % (user_id),
           {"originalVersionId": version})

@step(u'change the password to "(.*)" for the user with (that name|name "(.*)")')
def change_user_password(step, new_pw, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    user_id, version = get_user_resid(name)

    do_put(world.path_users + "%s/passwordchange/%s" % (user_id, new_pw),
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

    do_get(world.path_users + "current",
                  headers = headers, exp_status = 401)
    #
#    thisUser = get_single_item_from_endpoint("user",
#                                             world.path_users + "current",
#                                             headers = headers)


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
                                     world.path_users + "%s/assignments" % user_id)

    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for role in step.hashes:
        role_name = role["name"]
        found_perm = [x for x in assignment_list if x[ns("name")] == role_name]

        assert len(found_perm) == 1, "Expected to find assignment name %s in:\n%s" % (role_name,
                                                                                jstr(assignment_list))


