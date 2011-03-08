'''
Created on Jan 28, 2011

@author: camerondawson
'''
from features.tcm_data_helper import get_stored_or_store_name, eq_, ns, jstr
from features.tcm_request_helper import get_seed_product_id, do_post, \
    get_form_headers, get_auth_header_user_name, search_and_verify_existence, \
    get_testcase_resid, do_delete, get_testcase_latestversion_id, \
    get_list_from_endpoint, do_put, get_single_item_from_endpoint, \
    get_environment_resid, get_list_from_search, get_product_resid, \
    get_testcycle_resid, get_testrun_resid, get_testsuite_resid
from lettuce import step, world



'''
######################################################################

                     TEST CASE STEPS

######################################################################
'''

@step(u'create a new testcase with (that name|name "(.*)")')
def create_testcase_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("testcase", stored, name)

    post_payload = {"productId": get_seed_product_id(),
                    "maxAttachmentSizeInMbytes":"10",
                    "maxNumberOfAttachments":"5",
                    "name": name,
                    "description": "Lettuce tc"
                   }
    do_post(world.path_testcases,
            post_payload)


@step(u'user with (that name|name "(.*)") creates a new testcase with (that name|name "(.*)")')
def user_creates_testcase_with_name(step, stored_user, user_name, stored_testcase, testcase_name):
    user_name = get_stored_or_store_name("user", stored_user, user_name)
    testcase_name = get_stored_or_store_name("testcase", stored_testcase, testcase_name)

    post_payload = {"productId": get_seed_product_id(),
                    "maxAttachmentSizeInMbytes":"10",
                    "maxNumberOfAttachments":"5",
                    "name": testcase_name,
                    "description": "Lettuce tc"
                    }
    headers = get_form_headers(get_auth_header_user_name(user_name))
    do_post(world.path_testcases,
            post_payload,
            headers = headers)

@step(u'testcase with (that name|name "(.*)") (exists|does not exist)')
def check_testcase_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_name("testcase", stored, name)
    search_and_verify_existence(world.path_testcases,
                    {"name": name},
                     "testcase", existence)


@step(u'delete the testcase with (that name|name "(.*)")')
def delete_testcase_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("testcase", stored, name)

    testcase_id, version = get_testcase_resid(name)
    do_delete(world.path_testcases + str(testcase_id),
              {"originalVersionId": version})


@step(u'add these steps to the testcase with (that name|name "(.*)")')
def add_steps_to_testcase_name(step, stored, name):
    name = get_stored_or_store_name("testcase", stored, name)

    # first we need the testcase id so we can get the latest version to add steps to
    testcase_id = get_testcase_resid(name)[0]

    testcaseversion_id = get_testcase_latestversion_id(testcase_id)

    uri = world.path_testcases + "versions/" + str(testcaseversion_id) + "/steps/"
    for case_step in step.hashes:
        do_post(uri, case_step)

@step(u'the testcase with (that name|name "(.*)") has these steps')
def verify_testcase_steps(step, stored, name):
    name = get_stored_or_store_name("testcase", stored, name)

    # first we need the testcase id so we can get the latest version to add steps to
    testcase_id = get_testcase_resid(name)[0]

    testcaseversion_id = get_testcase_latestversion_id(testcase_id)

    # fetch the steps for this testcase from the latestversion

    uri = world.path_testcases + "versions/" + str(testcaseversion_id) + "/steps/"
    testcasestep_list = get_list_from_endpoint("testcasestep", uri)

    # compare the returned values with those passed in to verify match
    step_num = 0
    try:
        for exp_step in step.hashes:
            act_step = testcasestep_list[step_num]
            eq_(act_step[ns("name")], exp_step["name"], "name match")
            step_num += 1
    except KeyError:
        assert False, "Object field mismatch.\nExpected:\n" + jstr(step.hashes) + "\n\nActual:\n" + jstr(testcasestep_list)


@step(u'user with (that name|name "(.*)") approves the testcase with (that name|name "(.*)")')
def approve_testcase(step, stored_user, user_name, stored_testcase, testcase_name):
    testcase_name = get_stored_or_store_name("testcase", stored_testcase, testcase_name)
    user_name = get_stored_or_store_name("user", stored_user, user_name)

    # first we need the testcase id so we can get the latest version to approve
    testcase_id, version = get_testcase_resid(testcase_name)
    testcaseversion_id = get_testcase_latestversion_id(testcase_id)


    # do the approval of the testcase
    uri = world.path_testcases + "versions/%s/approve/" % (testcaseversion_id)
    headers = get_form_headers(get_auth_header_user_name(user_name))

    do_put(uri,
           {"originalVersionId": version},
            headers = headers)

#@todo: This has a hardcoded value for approvalStatusId, fix that
@step(u'the testcase with (that name|name "(.*)") has status of Active')
def testcase_has_status_of_approved(step, stored, testcase_name):
    testcase_name = get_stored_or_store_name("testcase", stored, testcase_name)

    # fetch the steps for this testcase from the latestversion
    testcase_id = get_testcase_resid(testcase_name)[0]
    testcaseversion = get_single_item_from_endpoint("testcaseversion",
                                            world.path_testcases + "%s/latestversion/" % (testcase_id))
    # should be just one
    try:
        eq_(testcaseversion[ns("approvalStatusId")], 2, "Testcase is approved: " + str(testcaseversion))
    except KeyError:
        assert False, "Object field mismatch.\nExpected:\n" + ns("approved") + "\n\nActual:\n" + jstr(testcaseversion)


@step(u'add environment "(.*)" to test case "(.*)"')
def add_environment_foo_to_test_case_bar(step, environment, test_case):
    # this takes 2 requests.
    #    1: get the id of this test case
    #    2: add the environment to the test case

    # fetch the test case's resource identity
    test_case_id, version = get_testcase_resid(test_case)

    post_payload = {"name": "test environment"}
    do_post(world.path_testcases + "%s/environments" % (test_case_id),
            post_payload,
            params = {"originalVersionId": version})

@step(u'remove environment "(.*)" from test case "(.*)"')
def remove_environment_from_test_case(step, environment, test_case):
    # fetch the test case's resource identity
    test_case_id, version = get_testcase_resid(test_case)
    environment_id = get_environment_resid(environment)

    do_delete(world.path_testcases + "%s/environments/%s" % (test_case_id, environment_id),
              {"originalVersionId": version})

@step(u'test case "(.*)" (has|does not have) environment "(.*)"')
def test_case_foo_has_environment_bar(step, test_case, haveness, environment):
    # fetch the test case's resource identity
    test_case_id = get_testcase_resid(test_case)[0]

    result_list = get_list_from_search("environment",
                                    world.path_testcases + "%s/environments" % test_case_id)

    found_item = [x for x in result_list if x[ns("name")] == environment]
    if (haveness == "has"):
        assert len(found_item) == 1, "Expected to find %s in:\n%s" % (environment,
                                                                 jstr(result_list))
    else:
        assert len(found_item) == 0, "Expected to NOT find %s in:\n%s" % (environment,
                                                                 jstr(result_list))


@step(u'test case with name "(.*)" (has|does not have) attachment with filename "(.*)"')
def test_case_foo_has_attachment_bar(step, test_case, haveness, attachment):
    # fetch the test case's resource identity
    test_case_id = get_testcase_resid(test_case)[0]

    result_list = get_list_from_search("attachment",
                                    world.path_testcases + "%s/attachments" % test_case_id)

    found_item = [x for x in result_list if x[ns("name")] == attachment]
    if (haveness == "has"):
        assert len(found_item) == 1, "Expected to find %s in:\n%s" % (attachment,
                                                                 jstr(result_list))
    else:
        assert len(found_item) == 0, "Expected to NOT find %s in:\n%s" % (attachment,
                                                                 jstr(result_list))


'''
######################################################################

                     TESTCYCLE STEPS

######################################################################
'''
@step(u'create a new testcycle with (that name|name "(.*)")')
def create_testcycle_with_name(step, stored, name):
    name = get_stored_or_store_name("testcycle", stored, name)

    post_payload = {"name": name,
                    "description": "Ahh, the cycle of life...",
                    "productId": get_seed_product_id(),
                    "startDate": "2011/02/02",
                    "communityAuthoringAllowed": "true",
                    "communityAccessAllowed": "true",
                    "endDate": "2014/02/02"
                   }

    do_post(world.path_testcycles,
            post_payload)

@step(u'create the following new testcycles:')
def create_testcycles(step):

    for item in step.hashes:
        # must do this or it will freak out the lettuce reporting, because
        # we delete items from this before submitting.
        testcycle = item.copy()
        # persist the last one we make.  Sometimes we will only make one.
        world.names["testcycle"] = testcycle["name"]

        # get the product id from the passed product name
        product_id = get_product_resid(testcycle["product name"])[0]

        testcycle["productId"] = product_id

        if testcycle.has_key('product name'):
            del testcycle['product name']

        do_post(world.path_testcycles,
                testcycle)


@step(u'testcycle with (that name|name "(.*)") (exists|does not exist)')
def check_testcycle_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_name("testcycle", stored, name)
    search_and_verify_existence(world.path_testcycles,
                    {"name": name},
                     "testcycle", existence)


@step(u'delete the testcycle with (that name|name "(.*)")')
def delete_testcycle_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("testcycle", stored, name)

    testcycle_id, version = get_testcycle_resid(name)

    do_delete(world.path_testcycles + str(testcycle_id),
                                  {"originalVersionId": version})

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

    do_post(world.path_testruns,
            post_payload)



@step(u'testrun with (that name|name "(.*)") (exists|does not exist)')
def check_testrun_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_name("testrun", stored, name)
    search_and_verify_existence(world.path_testruns,
                    {"name": name},
                     "testrun", existence)


@step(u'delete the testrun with (that name|name "(.*)")')
def delete_testrun_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("testrun", stored, name)

    testrun_id, version = get_testrun_resid(name)

    do_delete(world.path_testruns + str(testrun_id),
              {"originalVersionId": version})


@step(u'testcycle with name "(.*)" has the testrun with name "(.*)"')
def testcycle_has_testrun(step, cycle_name, run_name):

    testcycle_id = get_testcycle_resid(cycle_name)[0]

    uri = world.path_testcycles + "%s/testruns/" % testcycle_id
    testrun_list = get_list_from_endpoint("testrun", uri)

    found_run = [x for x in testrun_list if x[ns("name")] == run_name]
    assert len(found_run) == 1, "Expected to find name %s in:\n%s" % (run_name,
                                                                      jstr(testrun_list))




'''
######################################################################

                     TESTSUITE STEPS

######################################################################
'''

@step(u'create a new testsuite with (that name|name "(.*)")')
def create_testsuite_with_name(step, stored, name):
    name = get_stored_or_store_name("testsuite", stored, name)

    post_payload = {"productId": get_seed_product_id(),
                    "name": name,
                    "description": "Sweet Relief",
                    "useLatestVersions": "true"
                   }

    do_post(world.path_testsuites,
            post_payload)



@step(u'testsuite with (that name|name "(.*)") (exists|does not exist)')
def check_testsuite_foo_existence(step, stored, name, existence):
    name = get_stored_or_store_name("testsuite", stored, name)
    search_and_verify_existence(world.path_testsuites,
                    {"name": name},
                     "testsuite", existence)


@step(u'delete the testsuite with (that name|name "(.*)")')
def delete_testsuite_with_name_foo(step, stored, name):
    name = get_stored_or_store_name("testsuite", stored, name)

    testsuite_id, version = get_testsuite_resid(name)

    do_delete(world.path_testsuites + str(testsuite_id),
              {"originalVersionId": version})






