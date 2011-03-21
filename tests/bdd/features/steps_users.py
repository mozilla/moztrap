'''
Created on Jan 28, 2011

@author: camerondawson
'''
from features.models import UserModel, CompanyModel
from features.tcm_data_helper import compare_dicts_by_keys, ns_keys, \
    get_stored_or_store_name, get_user_status_id, ns, get_user_password, eq_, jstr
from features.tcm_request_helper import do_get, do_put, get_resource_identity, \
    get_json_headers, get_auth_header, do_put_for_cookie
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
    userModel = UserModel()
    created_obj = userModel.create(user_obj)

    compare_dicts_by_keys(ns_keys(user_obj),
                          created_obj,
                          ("firstName", "lastName", "email", "screenName", "companyId"))


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
                "companyId":CompanyModel().get_seed_resid()[0],
    }
    create_user_from_obj(user_obj)

'''
######################################################################

                     USER STEPS

######################################################################
'''


@step(u'create a new user with (that name|name "(.*)")')
def create_user_with_name_foo(step, stored, name):
    userModel = UserModel()
    name = userModel.get_stored_or_store_name(stored, name)
    create_user_from_name(name)

@step(u'get that newly created user by id')
def get_new_user_by_id(step):
    userModel = UserModel()
    last_created_user = userModel.get_latest_stored()
    user_id = get_resource_identity(last_created_user)[0]
    user_obj = userModel.get_by_id(user_id)

    compare_dicts_by_keys(last_created_user,
                          user_obj,
                          ("firstName", "lastName", "email", "screenName", "companyId"))

@step(u'update the user with (that name|name "(.*)") to have these values')
def update_user_with_name(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)


    user_id, version = UserModel().get_resid(name)

    new_values = step.hashes[0].copy()
    company_id = CompanyModel().get_resid(new_values["company name"])
    new_values["companyId"] = company_id
    del new_values["company name"]
    new_values["originalVersionId"] = version

    do_put(UserModel().root_path + "/" + str(user_id), new_values)

@step(u'user with (that name|name "(.*)") has these values')
def user_with_name_has_values(step, stored, name):
    userModel = UserModel()
    name = userModel.get_stored_or_store_name(stored, name)
    act_user = userModel.get_by_name(name)

    exp_user = step.hashes[0].copy()
    userModel.check_values(act_user, exp_user)

@step(u'that user has these values')
def last_referenced_user_has_values(step):
    userModel = UserModel()
    act_user = userModel.get_latest_stored()
    # fetch the latest values for this user
    act_user = userModel.get_by_id(get_resource_identity(act_user)[0])

    exp_user = step.hashes[0].copy()
    userModel.check_values(act_user, exp_user)

@step(u'change the email to "(.*)" for the user with (that name|name "(.*)")')
def change_user_email(step, new_email, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    user_id, version = UserModel().get_resid(name)

    do_put(UserModel().root_path + "/" + "%s/emailchange/%s" % (user_id, new_email),
           {"originalVersionId": version})

@step(u'confirm the email for the user with (that name|name "(.*)")')
def confirm_user_email(step, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    user_id, version = UserModel().get_resid(name)

    do_put(UserModel().root_path + "/" + "%s/emailconfirm" % (user_id),
           {"originalVersionId": version})

@step(u'change the password to "(.*)" for the user with (that name|name "(.*)")')
def change_user_password(step, new_pw, stored, name):
    name = get_stored_or_store_name("user", stored, name)
    user_id, version = UserModel().get_resid(name)

    do_put(UserModel().root_path + "/" + "%s/passwordchange/%s" % (user_id, new_pw),
           {"originalVersionId": version})


@step(u'log out the user with (that name|name "(.*)")')
def log_out(step, stored, user_name):
    user_name = get_stored_or_store_name("user", stored, user_name)

    headers = {'cookie': world.auth_cookie,
               'Content-Type':'application/json' }

    return do_put(UserModel().root_path + "/" + "logout", "", headers)


@step(u'log in user with (that name|name "(.*)")')
def log_in_with_name(step, stored, name):
    userModel = UserModel()
    name = userModel.get_stored_or_store_name(stored, name)

    cookie = userModel.log_user_in(name)[1]
    # store the cookie in world
    world.auth_cookie = cookie

@step(u'log in user with these credentials')
def log_in_with_credentials(step):
    user = step.hashes[0]
    headers = get_json_headers(get_auth_header(user["email"], user["password"]))

    cookie = do_put_for_cookie(UserModel().root_path + "/" + "login", "", headers)[1]
    world.auth_cookie = cookie
    # store the cookie in world

@step(u'logged in as the user with (that name|name "(.*)")')
def logged_in_as_user(step, stored, name):
    userModel = UserModel()
    name = userModel.get_stored_or_store_name(stored, name)
    names = name.split()

    thisUser = userModel.get_logged_in_user()

    eq_(thisUser[ns("firstName")], names[0], "First Name field didn't match")
    eq_(thisUser[ns("lastName")], names[1], "Last Name field didn't match")

@step(u'that user is not logged in')
def user_not_logged_in(step):
    headers = {'cookie': world.auth_cookie,
               'Content-Type':'application/json' }

    do_get(UserModel().root_path + "/" + "current",
                  headers = headers, exp_status = 401)
    #
#    thisUser = get_single_item_from_endpoint("user",
#                                             world.path_users + "current",
#                                             headers = headers)


@step(u'user with (that name|name "(.*)") (exists|does not exist)')
def check_user_existence(step, stored, name, existence):
    userModel = UserModel()
    name = userModel.get_stored_or_store_name(stored, name)
    names = name.split()
    userModel.verify_existence_on_root(existence = existence,
                                       params = {"firstName": names[0],
                                                 "lastName": names[1]})

@step(u'user with (that name|name "(.*)") is (active|inactive|disabled)')
def check_user_activated(step, stored, name, userStatus):
    userModel = UserModel()
    name = userModel.get_stored_or_store_name(stored, name)
    names = name.split()
    statusId = get_user_status_id(userStatus)

    userModel.verify_found_on_root(params = {"firstName": names[0],
                                             "lastName": names[1],
                                             "userStatusId": statusId})


@step(u'(activate|deactivate) the user with (that name|name "(.*)")')
def activate_user(step, status_action, stored, name):
    '''
        Users are not deleted, they're just registered or unregistered.
    '''
    userModel = UserModel()
    name = userModel.get_stored_or_store_name(stored, name)

    if (status_action == "activate"):
        userModel.activate(name)
    else:
        userModel.deactivate(name)


@step(u'user with (that name| name "(.*)") has at least these assignments:')
def foo_has_these_assignments(step, stored, name):
    userModel = UserModel()
    name = userModel.get_stored_or_store_name(stored, name)

    user_id = userModel.get_resid(name)[0]
    assignment_list = userModel.get_assignment_list(user_id)

    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for role in step.hashes:
        role_name = role["name"]
        found_perm = [x for x in assignment_list if x[ns("name")] == role_name]

        assert len(found_perm) == 1, "Expected to find assignment name %s in:\n%s" % (role_name,
                                                                                jstr(assignment_list))


