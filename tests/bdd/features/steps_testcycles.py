'''
Created on Mar 23, 2011

@author: camerondawson
'''
from features.models import TestcycleModel, ProductModel, UserModel
from features.tcm_data_helper import get_result_status_id, \
    verify_single_item_in_list, ns, jstr, eq_list_length
from features.tcm_request_helper import get_resource_identity
from lettuce.decorators import step


'''
######################################################################

                     TESTCYCLE STEPS

######################################################################
'''
@step(u'create a new testcycle with (that name|name "(.*)")')
def create_testcycle_with_name(step, stored, name):
    testcycleModel = TestcycleModel()
    name = testcycleModel.get_stored_or_store_name(stored, name)

    post_payload = {"name": name,
                    "description": "Ahh, the cycle of life...",
                    "productId": ProductModel().get_seed_resid()[0],
                    "startDate": "2011/02/02",
                    "communityAuthoringAllowed": "true",
                    "communityAccessAllowed": "true",
                    "endDate": "2014/02/02"
                   }
    testcycleModel.create(post_payload)

@step(u'create the following new testcycles:')
def create_testcycles(step):
    testcycleModel = TestcycleModel()

    for item in step.hashes:
        # must do this or it will freak out the lettuce reporting, because
        # we delete items from this before submitting.
        testcycle = item.copy()

        # get the product id from the passed product name
        product_id = ProductModel().get_resid(testcycle["product name"])[0]

        testcycle["productId"] = product_id

        if testcycle.has_key('product name'):
            del testcycle['product name']

        testcycleModel.create(testcycle)



@step(u'delete the testcycle with (that name|name "(.*)")')
def delete_testcycle_with_name_foo(step, stored, name):
    testcycleModel = TestcycleModel()
    name = testcycleModel.get_stored_or_store_name(stored, name)

    testcycleModel.delete(name)

@step(u'activate the testcycle with (that name|name "(.*)")')
def activate_testcycle_with_name(step, stored, name):
    testcycleModel = TestcycleModel()
    name = testcycleModel.get_stored_or_store_name(stored, name)

    testcycleModel.activate(name)


@step(u'testcycle with (that name|name "(.*)") (exists|does not exist)')
def check_testcycle_existence(step, stored, name, existence):
    testcycleModel = TestcycleModel()
    name = testcycleModel.get_stored_or_store_name(stored, name)

    testcycleModel.verify_existence_on_root(name,
                                            existence = existence)


@step(u'(that testcycle|the testcycle with name "(.*)") has the following result status summary counts')
def testcycle_has_summary_counts(step, stored_testcycle, testcycle_name):
    testcycleModel = TestcycleModel()
    testcycle = testcycleModel.get_stored_or_store_obj(stored_testcycle, testcycle_name)
    testcycle_id = get_resource_identity(testcycle)[0]

    # get the list of testcases for this testcycle
    summary_list = testcycleModel.get_summary_list(testcycle_id)

    eq_list_length(summary_list, step.hashes)

    # walk through and verify that each testcase has the expected status
    for category in step.hashes:
        # find that in the list of testcases
        status_id = get_result_status_id(category["name"])
        categoryInfo = verify_single_item_in_list(summary_list, "categoryName",
                                                  status_id)
        assert str(categoryInfo[ns("categoryValue")]) == category["count"], \
            "%s count was wrong.  Expected categoryName: %s , categoryValue: %s:\n%s" % \
            (category["name"], status_id, category["count"], jstr(categoryInfo))

@step(u'approve all the results for (that testcycle|the testcycle with name "(.*)")')
def approve_all_results_for_testcycle(step, stored_testcycle, testcycle_name):
    testcycleModel = TestcycleModel()
    testcycle = testcycleModel.get_stored_or_store_obj(stored_testcycle, testcycle_name)

    testcycleModel.approve_all_results(testcycle)

@step(u'(that testcycle|the testcycle with name "(.*)") has (no|the following) environmentgroups')
def testcycle_has_environmentgroups(step, stored_testcycle, testcycle_name, expect_any):
    testcycleModel = TestcycleModel()
    testcycle = testcycleModel.get_stored_or_store_obj(stored_testcycle, testcycle_name)
    testcycle_id = get_resource_identity(testcycle)[0]

    # get the list of testcases for this testcycle
    envgrp_list = testcycleModel.get_environmentgroup_list(testcycle_id)

    # this checks that the lengths match.  The expect_any holder is not used, but it allows for
    # alternate wording in the step.
    eq_list_length(envgrp_list, step.hashes)

    # walk through and verify that each testcase has the expected status
    for envgrp in step.hashes:
        # find that in the list of testcases
        exp_name = envgrp["name"]

        verify_single_item_in_list(envgrp_list,
                                   "name",
                                   exp_name)

@step(u'(that testcycle|the testcycle with name "(.*)") has (no|the following) testruns')
def testcycle_has_testruns(step, stored_testcycle, testcycle_name, expect_any):
    testcycleModel = TestcycleModel()
    testcycle = testcycleModel.get_stored_or_store_obj(stored_testcycle, testcycle_name)
    testcycle_id = get_resource_identity(testcycle)[0]

    # get the list of testcases for this testcycle
    testrun_list = testcycleModel.get_testrun_list(testcycle_id)

    eq_list_length(testrun_list, step.hashes)

    # walk through and verify that each testcase has the expected status
    for testrun in step.hashes:
        # find that in the list of testcases
        exp_name = testrun["name"]

        verify_single_item_in_list(testrun_list,
                                   "name",
                                   exp_name)


@step(u'add the following users to the testcycle with (that name|name "(.*)")')
def add_users_to_testcycle(step, stored, testcycle_name):
    testcycleModel = TestcycleModel()
    testcycle_name = testcycleModel.get_stored_or_store_name(stored, testcycle_name)

    user_ids = []
    for user in step.hashes:
        user_id = UserModel().get_resid(user["name"])[0]
        user_ids.append(user_id)

    testcycleModel.add_team_members(testcycle_name, user_ids)


@step(u'(that testcycle|the testcycle with name "(.*)") has (no|the following) team members')
def testcycle_has_team_members(step, stored_testcycle, testcycle_name, expect_any):
    testcycleModel = TestcycleModel()
    testcycle = testcycleModel.get_stored_or_store_obj(stored_testcycle, testcycle_name)
    testcycle_id = get_resource_identity(testcycle)[0]

    teammember_list = testcycleModel.get_team_members_list(testcycle_id)

    eq_list_length(teammember_list, step.hashes)

    for teammember in step.hashes:
        names = teammember["name"].split()

        verify_single_item_in_list(teammember_list,
                                   params = {"firstName": names[0],
                                             "lastName": names[1]}
                                   )


















