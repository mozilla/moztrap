'''
Created on Mar 9, 2011

@author: camerondawson
'''
from features.models import TestcaseModel, UserModel, TestcycleModel, \
    TestrunModel
from features.tcm_data_helper import ns, jstr, verify_single_item_in_list, \
    compare_dicts_by_keys, get_approval_status_id, eq_, get_result_status_id, \
    eq_list_length
from features.tcm_request_helper import get_resource_identity
from lettuce import step


'''
######################################################################

                     TESTRUN STEPS

######################################################################
'''

@step(u'create a new testrun with (that name|name "(.*)") with testcycle "(.*)"')
def create_testrun_with_name(step, stored, name, testcycle_name):
    testrunModel = TestrunModel()
    name = testrunModel.get_stored_or_store_name(stored, name)

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

    testrunModel.create(post_payload)


@step(u'testrun with (that name|name "(.*)") (exists|does not exist)')
def check_testrun_existence(step, stored, name, existence):
    testrunModel = TestrunModel()
    name = testrunModel.get_stored_or_store_name(stored, name)
    testrunModel.search_and_verify_existence(testrunModel.root_path,
                    {"name": name},
                    existence)


@step(u'delete the testrun with (that name|name "(.*)")')
def delete_testrun_with_name(step, stored, name):
    testrunModel = TestrunModel()
    name = testrunModel.get_stored_or_store_name(stored, name)

    testrunModel.delete(name)

@step(u'activate the testrun with (that name|name "(.*)")')
def activate_testrun_with_name(step, stored, name):
    testrunModel = TestrunModel()
    name = testrunModel.get_stored_or_store_name(stored, name)

    testrunModel.activate(name)


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
    testrunModel = TestrunModel()
    testrun_name = testrunModel.get_stored_or_store_name(stored, testrun_name)

    for tc in step.hashes:
        testrunModel.add_testcase(testrun_name, tc["testcase"])

@step(u'that testrun has the following results')
def testrun_has_results(step, stored, testrun_name):
    #{id}/reports/coverage/resultstatus
    assert False, "need implementation"

@step(u'add the following users to the testrun with (that name|name "(.*)")')
def add_users_to_testrun(step, stored, testrun_name):
    testrunModel = TestrunModel()
    testrun_name = testrunModel.get_stored_or_store_name(stored, testrun_name)

    user_ids = []
    for user in step.hashes:
        user_id = UserModel().get_resid(user["name"])[0]
        user_ids.append(user_id)

    testrunModel.add_team_members(testrun_name, user_ids)

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


@step(u'(that testrun|the testrun with name "(.*)") has the following team members')
def testrun_has_team_members(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    teammember_list = testrunModel.get_team_members_list(testrun_id)

    eq_list_length(teammember_list, step.hashes)

    for teammember in step.hashes:
        names = teammember["name"].split()

        verify_single_item_in_list(teammember_list,
                                   params = {"firstName": names[0],
                                             "lastName": names[1]}
                                   )


@step(u'fetch the following testcase results for (that testrun|the testrun with name "(.*)") by their ids')
def fetch_results_by_ids(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testcaseModel = TestcaseModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    for testcase in step.hashes:
        # for each testcase name, fetch the result that matches it in the testrun list
        testcase_obj = testcaseModel.get_by_name(testcase["name"])
        testcase_id = get_resource_identity(testcase_obj)[0]

        result_from_list = testrunModel.get_result(testcase_id,
                                                   testrun_id = testrun_id)
        testresult_id = get_resource_identity(result_from_list)[0]
        result_from_endpoint = testrunModel.get_result_by_id(testresult_id)
        compare_dicts_by_keys(result_from_list, result_from_endpoint, ("testCaseId", "testRunId", "testSuiteId"))

@step(u'approve the following testcase results for (that testrun|the testrun with name "(.*)")')
def approve_result_for_testrun(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testcaseModel = TestcaseModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    for testcase in step.hashes:
        testcase_id = testcaseModel.get_resid(testcase["name"])[0]

        testrunModel.approve_result(testrun_id, testcase_id)

@step(u'approve all the results for (that testrun|the testrun with name "(.*)")')
def approve_all_results_for_testrun(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)

    testrunModel.approve_all_results(testrun)

@step(u'results for (that testrun|the testrun with name "(.*)") have the following approval statuses')
def testrun_results_have_approval_statuses(step, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testcaseModel = TestcaseModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)
    testrun_id = get_resource_identity(testrun)[0]

    for testcase in step.hashes:
        testcase_id = testcaseModel.get_resid(testcase["name"])[0]

        result_obj = testrunModel.get_result(testcase_id, testrun_id)
        eq_(result_obj[ns("approvalStatusId")],
            get_approval_status_id(testcase["status"]),
            "Wrong approvalStatusId for result.  Expected:\n%s" % testcase)


@step(u'call retest (all|only failed) for (that testrun|the testrun with name "(.*)")')
def retest_for_testrun(step, scope, stored_testrun, testrun_name):
    testrunModel = TestrunModel()
    testrun = testrunModel.get_stored_or_store_obj(stored_testrun, testrun_name)

    only_failed = (scope == "only failed")

    testrunModel.retest(testrun,
                        only_failed = only_failed)

@step(u'call retest on the following testcases for (that testrun|the testrun with name "(.*)")')
def retest_for_testcases(step, stored_testrun, testrun_name):
    '''
        Step hashes can have a user name field or not.  If it's not specified, it will,
        obviously, not pass a user id, so it will assign the new result object to the
        user of the previous result.
    '''
    trModel = TestrunModel()
    testrun = trModel.get_stored_or_store_obj(stored_testrun, testrun_name)

    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    includedtestcase_list = trModel.get_included_testcases(testrun_id)

    for tc in step.hashes:
        testcase_id = TestcaseModel().get_resid(tc["name"])[0]

        try:
            tester_id = UserModel().get_resid(tc["user name"])[0]

        except KeyError:
            tester_id = None

        result = trModel.get_result(testcase_id,
                                    includedtestcase_list = includedtestcase_list)

        result_id = get_resource_identity(result)[0]

        trModel.retest_single(result_id, tester_id)


@step(u'the following testcases have the following result statuses for (that testrun|the testrun with name "(.*)")')
def testcases_have_result_statuses(step, stored_testrun, testrun_name):
    trModel = TestrunModel()
    testrun = trModel.get_stored_or_store_obj(stored_testrun, testrun_name)

    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    includedtestcase_list = trModel.get_included_testcases(testrun_id)

    for tc in step.hashes:
        testcase_id = TestcaseModel().get_resid(tc["name"])[0]

        result = trModel.get_result(testcase_id,
                                    includedtestcase_list = includedtestcase_list)

        # ok, we have the tc result in question, now check that its status matches expectations
        eq_(result[ns("testRunResultStatusId")],
            get_result_status_id(tc["status"]),
            "testRunResultStatusId check")

@step(u'the following testcases have pending result statuses for (that testrun|the testrun with name "(.*)")')
def testcases_have_pending_result_statuses(step, stored_testrun, testrun_name):
    trModel = TestrunModel()
    testrun = trModel.get_stored_or_store_obj(stored_testrun, testrun_name)

    testrun_id = get_resource_identity(testrun)[0]
    status_id = get_result_status_id("Pending")
    # get the list of testcases for this testrun
    result_list = trModel.search_for_results_by_result_status(testrun_id,
                                                              status_id)

    eq_list_length(result_list, step.hashes)

    for tc in step.hashes:
        testcase_id = TestcaseModel().get_resid(tc["name"])[0]

        result = verify_single_item_in_list(result_list, "testCaseId", testcase_id)

        # ok, we have the tc result in question, now check that its status matches expectations
        eq_(result[ns("testRunResultStatusId")],
            status_id,
            "testRunResultStatusId check")

@step(u'the following testcases have the following environments for (that testrun|the testrun with name "(.*)")')
def testcases_have_environments(step, stored_testrun, testrun_name):
    trModel = TestrunModel()
    testrun = trModel.get_stored_or_store_obj(stored_testrun, testrun_name)

    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    includedtestcase_list = trModel.get_included_testcases(testrun_id)

    for tc in step.hashes:
        testcase_id = TestcaseModel().get_resid(tc["name"])[0]

        result = trModel.get_result(testcase_id,
                                    includedtestcase_list = includedtestcase_list)
        testresult_id = get_resource_identity(result)[0]
        environments_list = trModel.get_result_environments_list(testresult_id)

        verify_single_item_in_list(environments_list, "name", tc["environment"])

@step(u'(that testrun|the testrun with name "(.*)") has the following result status summary counts')
def testrun_has_summary_counts(step, stored_testrun, testrun_name):
    trModel = TestrunModel()

    testrun = trModel.get_stored_or_store_obj(stored_testrun, testrun_name)

    testrun_id = get_resource_identity(testrun)[0]

    # get the list of testcases for this testrun
    summary_list = trModel.get_summary_list(testrun_id)

    # walk through and verify that each testcase has the expected status
    for category in step.hashes:
        # find that in the list of testcases
        status_id = get_result_status_id(category["name"])
        categoryInfo = verify_single_item_in_list(summary_list, "categoryName",
                                                  status_id)
        assert str(categoryInfo[ns("categoryValue")]) == category["count"], \
            "%s count was wrong.  Expected categoryName: %s , categoryValue: %s:\n%s" % \
            (category["name"], status_id, category["count"], jstr(categoryInfo))





