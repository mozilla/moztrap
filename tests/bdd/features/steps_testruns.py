'''
Created on Mar 9, 2011

@author: camerondawson
'''
from features.models import TestcaseModel, UserModel, TestcycleModel, \
    TestrunModel
from features.tcm_data_helper import get_stored_or_store_name, ns, jstr, \
    verify_single_item_in_list, json_to_obj
from features.tcm_request_helper import do_post, do_delete, do_put, do_get, \
    get_resource_identity
from lettuce import step, world


'''
######################################################################

                     TESTRUN STEPS

######################################################################
'''

@step(u'create a new testrun with (that name|name "(.*)") with testcycle "(.*)"')
def create_testrun_with_name(step, stored, name, testcycle_name):
    name = get_stored_or_store_name("testrun", stored, name)

    testcycle_id = TestcycleModel().get_resid(testcycle_name)[0]

    post_payload = {"testCycleId": testcycle_id,
                    "name": name,
                    "description": "Yeah, I'm gonna run to you...",
                    "selfAssignAllowed": "true",
                    "selfAssignPerEnvironment": "true",
                    "selfAssignLimit": 10,
                    "useLatestVersions": "true",
                    "startDate": "2011/02/02",
                    "endDate": "2012/02/02",
                    "autoAssignToTeam": "true"
                   }

    data = do_post(world.path_testruns,
                   post_payload)
    tcm_obj = json_to_obj(data)
    TestrunModel().store_latest(tcm_obj[ns("testrun")][0])


@step(u'testrun with (that name|name "(.*)") (exists|does not exist)')
def check_testrun_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_name("testrun", stored, name)
    TestrunModel().search_and_verify_existence(world.path_testruns,
                    {"name": name},
                    existence)


@step(u'delete the testrun with (that name|name "(.*)")')
def delete_testrun_with_name(step, stored, name):
    name = get_stored_or_store_name("testrun", stored, name)

    testrun_id, version = TestrunModel().get_resid(name)

    do_delete(world.path_testruns + str(testrun_id),
              {"originalVersionId": version})

@step(u'activate the testrun with (that name|name "(.*)")')
def activate_testrun_with_name(step, stored, name):
    name = get_stored_or_store_name("testrun", stored, name)

    testrun_id, version = TestrunModel().get_resid(name)

    do_put(world.path_testruns + "%s/activate" % testrun_id,
              {"originalVersionId": version})


@step(u'testcycle with name "(.*)" has the testrun with name "(.*)"')
def testcycle_has_testrun(step, cycle_name, run_name):
    testcycleModel = TestcycleModel()
    testcycle_id = testcycleModel.get_resid(cycle_name)[0]

    testrun_list = testcycleModel.get_testrun_list(testcycle_id)

    found_run = [x for x in testrun_list if x[ns("name")] == run_name]
    assert len(found_run) == 1, "Expected to find name %s in:\n%s" % (run_name,
                                                                      jstr(testrun_list))

@step(u'add the following testcases to the testrun with (that name|name "(.*)")')
def add_testcases_to_testrun(step, stored, testrun_name):
    testrun_name = get_stored_or_store_name("testrun", stored, testrun_name)
    testrun_id, version = TestrunModel().get_resid(testrun_name)

    tcModel = TestcaseModel()

    for tc in step.hashes:
        tc_id = tcModel.get_resid(tc["testcase"])[0]

        uri = world.path_testruns + "%s/includedtestcases" % (testrun_id)
        do_post(uri,
                {"testCaseVersionId": tc_id,
                 "priorityId": 1,
                 "runOrder": 1,
                 "blocking": "false",
                 "originalVersionId": version})

@step(u'that testrun has the following results')
def testrun_has_results(step, stored, testrun_name):
    #{id}/reports/coverage/resultstatus
    assert False, "need implementation"

@step(u'add the following users to the testrun with (that name|name "(.*)")')
def add_users_to_testrun(step, stored, testrun_name):
    testrun_name = get_stored_or_store_name("testrun", stored, testrun_name)
    testrun_id, version = TestrunModel().get_resid(testrun_name)

    user_ids = []
    for user in step.hashes:
        user_id = UserModel().get_resid(user["name"])[0]
        user_ids.append(user_id)

    do_put(world.path_testruns + "%s/team/members" % (testrun_id),
           {"userIds": user_ids,
            "originalVersionId": version})


@step(u'(that testrun|the testrun with name "(.*)") has the following testsuites')
def testrun_has_testsuites(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    testsuite_list = testrunModel.get_testsuite_list(testrun_id)
    # walk through and verify that each testcase has the expected status
    for exp_suite in step.hashes:

        # find that in the list of testcases
        verify_single_item_in_list(testsuite_list, "name", exp_suite["name"])

@step(u'(that testrun|the testrun with name "(.*)") has the following included testcases')
def testrun_has_testcases(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    # get the list of testcases for this testrun
    includedtestcase_list = testrunModel.get_included_testcases(testrun_id)

    # walk through and verify that each testcase has the expected status
    for tc in step.hashes:
        testcase_id = TestcaseModel().get_resid(tc["name"])[0]
        # find that in the list of testcases
        verify_single_item_in_list(includedtestcase_list, "testCaseId", testcase_id)

@step(u'(that testrun|the testrun with name "(.*)") has the following components')
def testrun_has_components(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)

    testrun_id = get_resource_identity(testrun)[0]

    component_list = testrunModel.get_component_list(testrun_id)

    # walk through and verify that each testcase has the expected status
    for component in step.hashes:
        # find that in the list of testcases
        verify_single_item_in_list(component_list, "name", component["name"])



@step(u'set the following testcase statuses for the testrun with (that name|name "(.*)")')
def mark_testcase_status(step, stored_testrun, testrun_name):
    data = do_get(world.path_testruns + "results")
    assert False, data
