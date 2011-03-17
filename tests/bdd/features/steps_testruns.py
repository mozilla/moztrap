'''
Created on Mar 9, 2011

@author: camerondawson
'''
from features.tcm_data_helper import get_stored_or_store_name, eq_, ns, jstr, \
    verify_single_item_in_list, json_to_obj
from features.tcm_request_helper import get_testcycle_resid, do_post, \
    search_and_verify_existence, get_testrun_resid, do_delete, \
    get_list_from_endpoint, get_testcase_resid, do_put, \
    get_testcase_latestversion_resid, get_form_headers, get_auth_header_user_name, \
    do_get, get_user_resid, get_testsuite_resid, get_stored_or_store_obj, \
    get_resource_identity, tcmpath, store_latest_of_type
from lettuce import step, world


'''
######################################################################

                     TESTRUN STEPS

######################################################################
'''

@step(u'create a new testrun with (that name|name "(.*)") with testcycle "(.*)"')
def create_testrun_with_name(step, stored, name, testcycle_name):
    name = get_stored_or_store_name("testrun", stored, name)

    testcycle_id = get_testcycle_resid(testcycle_name)[0]

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
    store_latest_of_type("testrun", tcm_obj[ns("testrun")][0])


@step(u'testrun with (that name|name "(.*)") (exists|does not exist)')
def check_testrun_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_name("testrun", stored, name)
    search_and_verify_existence(world.path_testruns,
                    {"name": name},
                     "testrun", existence)


@step(u'delete the testrun with (that name|name "(.*)")')
def delete_testrun_with_name(step, stored, name):
    name = get_stored_or_store_name("testrun", stored, name)

    testrun_id, version = get_testrun_resid(name)

    do_delete(world.path_testruns + str(testrun_id),
              {"originalVersionId": version})

@step(u'activate the testrun with (that name|name "(.*)")')
def activate_testrun_with_name(step, stored, name):
    name = get_stored_or_store_name("testrun", stored, name)

    testrun_id, version = get_testrun_resid(name)

    do_put(world.path_testruns + "%s/activate" % testrun_id,
              {"originalVersionId": version})


@step(u'testcycle with name "(.*)" has the testrun with name "(.*)"')
def testcycle_has_testrun(step, cycle_name, run_name):

    testcycle_id = get_testcycle_resid(cycle_name)[0]

    uri = world.path_testcycles + "%s/testruns/" % testcycle_id
    testrun_list = get_list_from_endpoint("testrun", uri)

    found_run = [x for x in testrun_list if x[ns("name")] == run_name]
    assert len(found_run) == 1, "Expected to find name %s in:\n%s" % (run_name,
                                                                      jstr(testrun_list))

@step(u'add the following testcases to the testrun with (that name|name "(.*)")')
def add_testcases_to_testrun(step, stored, testrun_name):
    testrun_name = get_stored_or_store_name("testrun", stored, testrun_name)
    testrun_id, version = get_testrun_resid(testrun_name)

    for tc in step.hashes:
        tc_id, tc_ver = get_testcase_resid(tc["testcase"])
        tc_ver_id, tc_ver_ver = get_testcase_latestversion_resid(tc_id)

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
    testrun_id, version = get_testrun_resid(testrun_name)

    user_ids = []
    for user in step.hashes:
        user_id = get_user_resid(user["name"])[0]
        user_ids.append(user_id)

    do_put(world.path_testruns + "%s/team/members" % (testrun_id),
           {"userIds": user_ids,
            "originalVersionId": version})


@step(u'(that testrun|the testrun with name "(.*)") has the following testsuites')
def testrun_has_testsuites(step, stored_testrun, testrun_name):
    testrun = get_stored_or_store_obj("testrun", stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    testsuite_list = get_list_from_endpoint("testsuite",
                                                   tcmpath("testruns") + "%s/testsuites" %
                                                   testrun_id)
    # walk through and verify that each testcase has the expected status
    for exp_suite in step.hashes:

        # find that in the list of testcases
        verify_single_item_in_list(testsuite_list, "name", exp_suite["name"])

@step(u'(that testrun|the testrun with name "(.*)") has the following included testcases')
def testrun_has_testcases(step, stored_testrun, testrun_name):
    testrun = get_stored_or_store_obj("testrun", stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    # get the list of testcases for this testrun
    includedtestcase_list = get_list_from_endpoint("includedtestcase",
                                                   tcmpath("testruns") + "%s/includedtestcases" %
                                                   testrun_id)
    # walk through and verify that each testcase has the expected status
    for tc in step.hashes:
        testcase_id = get_testcase_resid(tc["name"])[0]
        # find that in the list of testcases
        verify_single_item_in_list(includedtestcase_list, "testCaseId", testcase_id)

@step(u'(that testrun|the testrun with name "(.*)") has the following components')
def testrun_has_components(step, stored_testrun, testrun_name):
    testrun = get_stored_or_store_obj("testrun", stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    # get the list of testcases for this testrun
    component_list = get_list_from_endpoint("component",
                                                   tcmpath("testruns") + "%s/components" %
                                                   testrun_id)
    # walk through and verify that each testcase has the expected status
    for component in step.hashes:
        # find that in the list of testcases
        verify_single_item_in_list(component_list, "name", component["name"])



@step(u'set the following testcase statuses for the testrun with (that name|name "(.*)")')
def mark_testcase_status(step, stored_testrun, testrun_name):
    data = do_get(world.path_testruns + "results")
    assert False, data
