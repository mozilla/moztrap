'''
Created on Jan 28, 2011

@author: camerondawson
'''
from features.models import EnvironmenttypeModel, EnvironmentModel, ProductModel, \
    EnvironmentgroupModel, TestrunModel, CompanyModel, TestcycleModel
from features.tcm_data_helper import get_stored_or_store_name, ns, jstr, eq_, \
    verify_single_item_in_list
from lettuce import step

'''
######################################################################

                     ENVIRONMENT STEPS

######################################################################
'''

@step(u'an environment with (that name|name "(.*)") (exists|does not exist)')
def check_environement_foo_existence(step, stored, name, existence):
    model = EnvironmentModel()
    name = model.get_stored_or_store_name(stored, name)
    model.verify_existence_on_root(name, existence = existence)

@step(u'an environmenttype with (that name|name "(.*)") (exists|does not exist)')
def check_environementtype_existence(step, stored, name, existence):
    model = EnvironmenttypeModel()
    name = model.get_stored_or_store_name(stored, name)
    model.verify_existence_on_root(name, existence = existence)

@step(u'an environmentgroup with (that name|name "(.*)") (exists|does not exist)')
def check_environementgroup_existence(step, stored, name, existence):
    model = EnvironmentgroupModel()
    name = model.get_stored_or_store_name(stored, name)
    model.verify_existence_on_root(name, existence = existence)

@step(u'a group environmenttype with (that name|name "(.*)") (exists|does not exist)')
def check_group_environement_foo_existence(step, stored, name, existence):
    model = EnvironmenttypeModel()
    name = model.get_stored_or_store_name(stored, name)

    model.verify_existence_on_root(name,
                                   existence = existence,
                                   params = {"name": name,
                                             "groupType": True})

@step(u'at least the following environments exist')
def at_least_these_environments_exist(step):
    model = EnvironmentModel()
    env_list = model.get_all_list()

    # walk through all the expected roles and make sure it has them all
    # note, it doesn't check that ONLY these roles exist.  That should be a different
    # method.
    for env in step.hashes:
        env_name = env["name"]
        envtype_id = EnvironmenttypeModel().get_resid(env["type"])[0]
        found_env = [x for x in env_list if ((x[ns("name")] == env_name) and (x[ns("environmentTypeId")] == envtype_id))]

        assert (len(found_env) == 1), \
            "Expected to find environment with name %s and environmentTypeId of %s in:\n%s" % \
            (env_name, envtype_id, jstr(env_list))

@step(u'create a new environment with (that name|name "(.*)") of type "(.*)"')
def create_environment_with_name(step, stored, name, type_name):
    '''
        This creates an environmenttype that applies to an environment object
    '''
    model = EnvironmentModel()
    name = model.get_stored_or_store_name(stored, name)

    type_resid = EnvironmenttypeModel().get_resid(type_name)[0]

    params = {
              "name": name,
              "companyId": CompanyModel().get_seed_resid()[0],
              "environmentTypeId": type_resid
              }

    model.create(params)


@step(u'delete the environment with (that name|name "(.*)")')
def delete_environment_with_name(step, stored, name):
    envModel = EnvironmentModel()
    name = envModel.get_stored_or_store_name(stored, name)
    envModel.delete(name)


@step(u'product with (that name|name "(.*)") (has|does not have) the environmentgroup with (that name|name "(.*)")')
def product_has_environementgroup(step, stored_prod, prod_name, haveness, stored_envgrp, envgrp_name):
    prod_name = get_stored_or_store_name("product", stored_prod, prod_name)
    envgrp_name  = get_stored_or_store_name("environmentgroup", stored_envgrp, envgrp_name)

    # this url needs to search for environment groups for that product
    # should be products/{id}/environmentgroups
    productModel = ProductModel()

    productModel.verify_has_environmentgroup(prod_name, envgrp_name,(haveness == "has"))


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
    envtypeModel = EnvironmenttypeModel()
    name = envtypeModel.get_stored_or_store_name(stored, name)

    post_payload = {
                    "name": name,
                    "groupType": groupType,
                    "companyId": CompanyModel().get_seed_resid()[0]
                    }
    envtypeModel.create(post_payload)

@step(u'delete the environmenttype with (that name|name "(.*)")')
def delete_environmenttype_with_name(step, stored, name):
    envtypeModel = EnvironmenttypeModel()
    name = envtypeModel.get_stored_or_store_name(stored, name)
    envtypeModel.delete(name)


@step(u'environmenttype with (that name|name "(.*)") is (a group|not a group) environmenttype')
def check_group_environmenttype_with_name(step, stored, name, is_group):
    envtypeModel = EnvironmenttypeModel()

    name = envtypeModel.get_stored_or_store_name(stored, name)
    groupType = (is_group.strip() == "a group")

    env_type = envtypeModel.get_by_name(name)

    eq_(env_type[ns("groupType")], groupType, "GroupType match check")

'''
######################################################################

                     ENVIRONMENT GROUP STEPS

######################################################################
'''
@step(u'create a new environmentgroup with (that name|name "(.*)") of type "(.*)"')
def create_environmentgroup_with_name(step, stored, name, type_name):
    model = EnvironmentgroupModel()
    name = model.get_stored_or_store_name(stored, name)

    type_resid = EnvironmenttypeModel().get_resid(type_name)[0]

    post_payload = {
                    "name": name,
                    "description": "oh, this old thing...",
                    "companyId": CompanyModel().get_seed_resid()[0],
                    "environmentTypeId": type_resid
                    }
    model.create(post_payload)

@step(u'create the following new environmentgroups')
def create_environmentgroups(step):
    model = EnvironmentgroupModel()

    for envgrp in step.hashes:

        type_resid = EnvironmenttypeModel().get_resid(envgrp["environmenttype name"],)[0]

        post_payload = {
                        "name": envgrp["name"],
                        "description": envgrp["description"],
                        "companyId": CompanyModel().get_seed_resid()[0],
                        "environmentTypeId": type_resid
                        }
        model.create(post_payload)

@step(u'delete the environmentgroup with (that name|name "(.*)")')
def delete_environmentgroup_with_name(step, stored, name):
    envgrpModel = EnvironmentgroupModel()
    name = envgrpModel.get_stored_or_store_name(stored, name)
    envgrpModel.delete(name)

@step(u'add the following environments to the environmentgroup with (that name|name "(.*)")')
def add_environment_to_environmentgroup(step, stored_envgrp, envgrp_name):
    envModel = EnvironmentModel()
    envgrpModel = EnvironmentgroupModel()

    envgrp_name = envgrpModel.get_stored_or_store_name(stored_envgrp, envgrp_name)
    envgrp_id, version = envgrpModel.get_resid(envgrp_name)

    env_ids = []
    for env in step.hashes:
        env_id = envModel.get_resid(env["name"])[0]
        env_ids.append(env_id)

    envgrpModel.add_environments(envgrp_id, version, env_ids)


@step(u'add the following environmentgroups to the testrun with (that name|name "(.*)")')
def add_envgroups_to_testrun(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testrun_name = testrunModel.get_stored_or_store_name(stored_testrun, testrun_name)

    envgrp_ids = []
    for envgrp in step.hashes:
        envgrp_id = EnvironmentgroupModel().get_resid(envgrp["name"])[0]
        envgrp_ids.append(envgrp_id)

    testrunModel.add_environmentgroups(testrun_name, envgrp_ids)

@step(u'add the following environmentgroups to the testcycle with (that name|name "(.*)")')
def add_envgroups_to_testcycle(step, stored_testcycle, testcycle_name):
    testcycleModel = TestcycleModel()
    testcycle_name = testcycleModel.get_stored_or_store_name(stored_testcycle, testcycle_name)

    envgrp_ids = []
    for envgrp in step.hashes:
        envgrp_id = EnvironmentgroupModel().get_resid(envgrp["name"])[0]
        envgrp_ids.append(envgrp_id)

    testcycleModel.add_environmentgroups(testcycle_name, envgrp_ids)

@step(u'add the following environmentgroups to the product with (that name|name "(.*)")')
def add_envgroups_to_product(step, stored_product, product_name):
    productModel = ProductModel()
    product_name = productModel.get_stored_or_store_name(stored_product, product_name)

    envgrp_ids = []
    for envgrp in step.hashes:
        envgrp_id = EnvironmentgroupModel().get_resid(envgrp["name"])[0]
        envgrp_ids.append(envgrp_id)

    productModel.add_environmentgroups(product_name, envgrp_ids)


@step(u'(that testrun|the testrun with name "(.*)") has the following environmentgroups')
def testrun_has_environments(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)
    testrun_id = testrunModel.get_resid(testrun[ns("name")])[0]

    envgrp_list = testrunModel.get_environmentgroup_list(testrun_id)

    # walk through and verify that each environment is included
    for envgrp in step.hashes:
        # find that in the list of items
        verify_single_item_in_list(envgrp_list, "name", envgrp["name"])

