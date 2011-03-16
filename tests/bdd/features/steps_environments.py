'''
Created on Jan 28, 2011

@author: camerondawson
'''
from features.tcm_data_helper import get_stored_or_store_name, ns, jstr, eq_, \
    verify_single_item_in_list
from features.tcm_request_helper import do_post, do_delete, get_list_from_search, \
    get_seed_company_id, search_and_verify_existence, get_environmenttype_resid, \
    get_environment_resid, get_product_resid, search_and_verify, \
    get_environmentgroup_resid, do_put, get_testrun_resid, get_stored_or_store_obj, \
    get_resource_identity, get_list_from_endpoint, tcmpath, get_testcase_resid
from lettuce import step, world

'''
######################################################################

                     ENVIRONMENT STEPS

######################################################################
'''

@step(u'an (environment|environmenttype|environmentgroup) with (that name|name "(.*)") (exists|does not exist)')
def check_environement_foo_existence(step, objtype, stored, name, existence):
    name = get_stored_or_store_name(objtype, stored, name)


    search_and_verify_existence(world.env_path_map[objtype],
                    {"name": name},
                    objtype, existence)

@step(u'a group environmenttype with (that name|name "(.*)") (exists|does not exist)')
def check_group_environement_foo_existence(step, stored, name, existence):
    objtype = "environmenttype"
    name = get_stored_or_store_name(objtype, stored, name)


    search_and_verify_existence(world.env_path_map[objtype],
                    {"name": name,
                     "groupType": True},
                     objtype, existence)

@step(u'at least the following environments exist')
def at_least_these_environments_exist(step):

    env_list = get_list_from_search("environment",
                                     world.path_environments)

    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for env in step.hashes:
        env_name = env["name"]
        envtype_id = get_environmenttype_resid(env["type"])[0]
        found_env = [x for x in env_list if ((x[ns("name")] == env_name) and (x[ns("environmentTypeId")] == envtype_id))]

        assert (len(found_env) == 1), \
            "Expected to find environment with name %s and environmentTypeId of %s in:\n%s" % \
            (env_name, envtype_id, jstr(env_list))

@step(u'create a new environment with (that name|name "(.*)") of type "(.*)"')
def create_environment_with_name(step, stored, name, type_name):
    '''
        This creates an environmenttype that applies to an environment object
    '''
    name = get_stored_or_store_name("environment", stored, name)

    type_resid = get_environmenttype_resid(type_name)[0]

    post_payload = {
                    "name": name,
                    "companyId": get_seed_company_id(),
                    "environmentTypeId": type_resid
                    }

    do_post(world.path_environments,
            post_payload)


@step(u'delete the environment with (that name|name "(.*)")')
def delete_environment_with_name(step, stored, name):
    name = get_stored_or_store_name("environment", stored, name)

    resid, version = get_environment_resid(name)

    do_delete(world.path_environments + str(resid),
              {"originalVersionId": version})


@step(u'product with (that name|name "(.*)") (has|does not have) the environmentgroup with (that name|name "(.*)")')
def product_has_environementgroup(step, stored_prod, prod_name, haveness, stored_envgrp, envgrp_name):
    prod_name = get_stored_or_store_name("product", stored_prod, prod_name)
    envgrp_name  = get_stored_or_store_name("environment", stored_envgrp, envgrp_name)

    # this url needs to search for environment groups for that product
    # should be products/{id}/environmentgroups

    resid = get_product_resid(prod_name)[0]


    uri = world.path_products + "/%s/environmentgroups" % resid
    search_and_verify(uri,
                      {"name": envgrp_name},
                      "environmentgroup",
                      (haveness == "has"))


'''
######################################################################

                     ENVIRONMENT TYPE STEPS

######################################################################
'''

@step(u'create a new (group environmenttype|environmenttype) with (that name|name "(.*)")')
def create_environmenttype_with_name(step, group, stored, name):
    '''
        This creates an environmenttype that applies to an environmentGroup object
    '''
    groupType = (group.strip() == "group environmenttype")
    name = get_stored_or_store_name("environmenttype", stored, name)

    post_payload = {
                    "name": name,
                    "groupType": groupType,
                    "companyId": get_seed_company_id()
                    }

    do_post(world.path_environmenttypes,
            post_payload)

@step(u'delete the environmenttype with (that name|name "(.*)")')
def delete_environmenttype_with_name(step, stored, name):
    name = get_stored_or_store_name("environmenttype", stored, name)

    resid, version = get_environmenttype_resid(name)
    do_delete(world.path_environmenttypes + str(resid),
              {"originalVersionId": version})


@step(u'environmenttype with (that name|name "(.*)") is (a group|not a group) environmenttype')
def check_group_environmenttype_with_name(step, stored, name, is_group):

    name = get_stored_or_store_name("environmenttype", stored, name)
    groupType = (is_group.strip() == "a group")

    resp_list = get_list_from_search("environmenttype",
                                world.path_environmenttypes,
                                {"name": name})
    # taking the first one
    env_type = resp_list[0]
    eq_(env_type[ns("groupType")], groupType, "GroupType match check")

'''
######################################################################

                     ENVIRONMENT GROUP STEPS

######################################################################
'''
@step(u'create a new environmentgroup with (that name|name "(.*)") of type "(.*)"')
def create_environmentgroup_with_name(step, stored, name, type_name):
    name = get_stored_or_store_name("environmentgroup", stored, name)

    type_resid = get_environmenttype_resid(type_name)[0]
    post_payload = {
                    "name": name,
                    "description": "oh, this old thing...",
                    "companyId": get_seed_company_id(),
                    "environmentTypeId": type_resid
                    }

    do_post(world.path_environmentgroups,
            post_payload)


@step(u'delete the environmentgroup with (that name|name "(.*)")')
def delete_environmentgroup_with_name(step, stored, name):
    name = get_stored_or_store_name("environmentgroup", stored, name)

    resid, version = get_environmentgroup_resid(name)

    do_delete(world.path_environmentgroups + str(resid),
                                            {"originalVersionId": version})

@step(u'add the following environments to the environmentgroup with (that name|name "(.*)")')
def add_environment_to_environmentgroup(step, stored_envgrp, envgrp_name):
    envgrp_name = get_stored_or_store_name("environmentgroup", stored_envgrp, envgrp_name)
    envgrp_resid, version = get_environmentgroup_resid(envgrp_name)

    env_ids = []
    for env in step.hashes:
        env_id = get_environment_resid(env["name"])[0]
        env_ids.append(env_id)

    do_put(world.path_environmentgroups + "%s/environments" % (envgrp_resid),
           {"environmentIds": env_ids,
            "originalVersionId": version})


@step(u'add the following environmentgroups to the testrun with (that name|name "(.*)")')
def add_envgroups_to_testrun(step, stored_testrun, testrun_name):
    testrun_name = get_stored_or_store_name("testrun", stored_testrun, testrun_name)
    testrun_resid, version = get_testrun_resid(testrun_name)

    envgrp_ids = []
    for envgrp in step.hashes:
        envgrp_id = get_environmentgroup_resid(envgrp["name"])[0]
        envgrp_ids.append(envgrp_id)

    do_put(world.path_testruns + "%s/environmentgroups" % (testrun_resid),
           {"environmentGroupIds": envgrp_ids,
            "originalVersionId": version})

@step(u'(that testrun|the testrun with name "(.*)") has the following environmentgroups')
def testrun_has_environments(step, stored_testrun, testrun_name):
    testrun = get_stored_or_store_obj("testrun", stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    # get the list of testcases for this testrun
    envgrp_list = get_list_from_endpoint("environmentgroup",
                                         tcmpath("testruns") + "%s/environmentgroups" %
                                         testrun_id)
    # walk through and verify that each environment is included
    for envgrp in step.hashes:
        # find that in the list of items
        verify_single_item_in_list(envgrp_list, "name", envgrp["name"])

