'''
Created on Jan 28, 2011

@author: camerondawson
'''
from features.models import TestcaseModel, UserModel, TestrunModel, ProductModel, \
    TestcycleModel, TestsuiteModel
from features.tcm_data_helper import get_stored_or_store_name, eq_, ns, jstr, \
    verify_single_item_in_list, get_result_status_id
from features.tcm_request_helper import get_form_headers, get_resource_identity
from lettuce import step, world



'''
######################################################################

                     TEST CASE STEPS

######################################################################
'''

@step(u'create a new testcase with (that name|name "(.*)")')
def create_testcase_with_name(step, stored, name):
    testcaseModel = TestcaseModel()
    name = testcaseModel.get_stored_or_store_name(stored, name)

    post_payload = {"productId": ProductModel().get_seed_resid()[0],
                    "maxAttachmentSizeInMbytes":"10",
                    "maxNumberOfAttachments":"5",
                    "name": name,
                    "description": "Lettuce tc"
                   }
    testcaseModel.create(post_payload)


@step(u'user with (that name|name "(.*)") creates a new testcase with (that name|name "(.*)")')
def user_creates_testcase_with_name(step, stored_user, user_name, stored_testcase, testcase_name):
    userModel = UserModel()
    user_name = userModel.get_stored_or_store_name(stored_user, user_name)
    testcaseModel = TestcaseModel()
    testcase_name = testcaseModel.get_stored_or_store_name(stored_testcase, testcase_name)

    post_payload = {"productId": ProductModel().get_seed_resid()[0],
                    "maxAttachmentSizeInMbytes":"10",
                    "maxNumberOfAttachments":"5",
                    "name": testcase_name,
                    "description": "Lettuce tc"
                    }
    headers = get_form_headers(userModel.get_auth_header(user_name))

    testcaseModel.create(post_payload, headers)

@step(u'testcase with (that name|name "(.*)") (exists|does not exist)')
def check_testcase_foo_existence(step, stored, name, existence):
    testcaseModel = TestcaseModel()
    name = testcaseModel.get_stored_or_store_name(stored, name)
    testcaseModel.verify_existence_on_root (name,
                                              existence = existence)


@step(u'delete the testcase with (that name|name "(.*)")')
def delete_testcase_with_name_foo(step, stored, name):
    testcaseModel = TestcaseModel()
    name = testcaseModel.get_stored_or_store_name(stored, name)

    testcaseModel.delete(name)


@step(u'add these steps to the testcase with (that name|name "(.*)")')
def add_steps_to_testcase_name(step, stored, name):
    testcaseModel = TestcaseModel()
    name = testcaseModel.get_stored_or_store_name(stored, name)
    # first we need the testcase id so we can get the latest version to add steps to
    testcase_id = testcaseModel.get_resid(name)[0]
    testcaseversion_id = testcaseModel.get_latestversion_resid(testcase_id)[0]

    testcaseModel.add_steps(testcaseversion_id, step.hashes)

@step(u'the testcase with (that name|name "(.*)") has these steps')
def verify_testcase_steps(step, stored, name):
    tcModel = TestcaseModel()
    name = tcModel.get_stored_or_store_name(stored, name)

    testcasestep_list = tcModel.get_latest_steps_list(name)

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
def user_approves_testcase(step, stored_user, user_name, stored_testcase, testcase_name):
    testcase_name = get_stored_or_store_name("testcase", stored_testcase, testcase_name)
    user_name = get_stored_or_store_name("user", stored_user, user_name)

    tcModel = TestcaseModel()
    tcModel.approve_by_user(testcase_name, user_name)

@step(u'user with (that name|name "(.*)") approves the following testcases')
def user_approves_testcases(step, stored_user, user_name):
    user_name = get_stored_or_store_name("user", stored_user, user_name)

    tcModel = TestcaseModel()

    for tc in step.hashes:
        tcModel.approve_by_user(tc["name"], user_name)

@step(u'assign the following testcases to the user with (that name|name "(.*)") for the testrun with (that name|name "(.*)")')
def assign_testcases_to_user_for_testrun(step, stored_user, user_name, stored_testrun, testrun_name):
    '''
        Expect hashes to contain:
        | testcase name |
    '''
    user_name = get_stored_or_store_name("user", stored_user, user_name)
    user_id = UserModel().get_resid(user_name)[0]
    testrun_name = get_stored_or_store_name("testrun", stored_testrun, testrun_name)
    trModel = TestrunModel()

    for tc in step.hashes:
        trModel.assign_testcase(testrun_name, user_id, tc["name"])



@step(u'activate the testcase with (that name|name "(.*)")')
def activate_testcase_with_name(step, stored, name):
    tcModel = TestcaseModel()
    name = tcModel.get_stored_or_store_name(stored, name)

    tcModel.activate(name)



@step(u'activate the following testcases')
def activate_testcases(step):

    tcModel = TestcaseModel()

    for tc in step.hashes:
        tcModel.activate(tc["name"])


#@todo: This has a hardcoded value for approvalStatusId, fix that
@step(u'the testcase with (that name|name "(.*)") has approval status of Active')
def testcase_has_status_of_approved(step, stored, testcase_name):
    tcModel = TestcaseModel()
    testcase_name = tcModel.get_stored_or_store_name(stored, testcase_name)

    # fetch the steps for this testcase from the latestversion
    testcase_id = tcModel.get_resid(testcase_name)[0]
    testcaseversion = tcModel.get_latestversion(testcase_id)
    # should be just one
    try:
        eq_(testcaseversion[ns("approvalStatusId")], 2, "Testcase is approved: " + str(testcaseversion))
    except KeyError:
        assert False, "Object field mismatch.\nExpected:\n" + ns("approved") + "\n\nActual:\n" + jstr(testcaseversion)

@step(u'the following testcases have the following approval statuses')
def testcases_have_approval_statuses(step):

    tcModel = TestcaseModel()

    for tc in step.hashes:
        testcase_id = tcModel.get_resid(tc["name"])[0]
        testcaseversion = tcModel.get_latestversion(testcase_id)
        # should be just one
        try:
            eq_(testcaseversion[ns("approvalStatusId")], 2, "Testcase is approved: " + str(testcaseversion))
        except KeyError:
            assert False, "Object field mismatch.\nExpected:\n" + ns("approved") + "\n\nActual:\n" + jstr(testcaseversion)


@step(u'user with (that name|name "(.*)") marks the following testcase result statuses for the testrun with (that name|name "(.*)")')
def user_marks_testcase_status(step, stored_user, user_name, stored_testrun, testrun_name):
    trModel = TestrunModel()
    testrun_name = trModel.get_stored_or_store_name(stored_testrun, testrun_name)
    userModel = UserModel()
    user_name = userModel.get_stored_or_store_name(stored_user, user_name)

    # first we need the testrun id so we can get the latest version to approve
#    user_id = UserModel().get_resid(user_name)[0]
    testrun_id = trModel.get_resid(testrun_name)[0]

    # get the list of testcases for this testrun
    includedtestcase_list = trModel.get_included_testcases(testrun_id)

    for tc in step.hashes:
        testcase_id = TestcaseModel().get_resid(tc["name"])[0]

        result_obj = trModel.get_result(testcase_id,
                                    includedtestcase_list = includedtestcase_list)
        result_id = get_resource_identity(result_obj)[0]

        started_result = trModel.start_testcase(result_obj, user_name)
        started_result_version = get_resource_identity(started_result)[1]
        # now finally mark it with the specified status

        trModel.set_testcase_status(result_id, started_result_version, user_name, tc["status"])


@step(u'testcase with name "(.*)" (has|does not have) attachment with filename "(.*)"')
def testcase_has_attachment(step, test_case, haveness, attachment):
    # fetch the test case's resource identity
    testcaseModel = TestcaseModel()
    testcase_id = testcaseModel.get_resid(test_case)[0]

    result_list = testcaseModel.get_attachment_list(testcase_id)

    #@todo: this should be abstracted into a helper method or in the model
    found_item = [x for x in result_list if x[ns("name")] == attachment]
    if (haveness == "has"):
        assert len(found_item) == 1, "Expected to find %s in:\n%s" % (attachment,
                                                                 jstr(result_list))
    else:
        assert len(found_item) == 0, "Expected to NOT find %s in:\n%s" % (attachment,
                                                                 jstr(result_list))




'''
######################################################################

                     TESTSUITE STEPS

######################################################################
'''

@step(u'create a new testsuite with (that name|name "(.*)")')
def create_testsuite_with_name(step, stored, name):
    testsuiteModel = TestsuiteModel()
    name = testsuiteModel.get_stored_or_store_name(stored, name)

    post_payload = {"productId": ProductModel().get_seed_resid()[0],
                    "name": name,
                    "description": "Sweet Relief",
                    "useLatestVersions": "true"
                   }
    testsuiteModel.create(post_payload)

@step(u'create the following new testsuites:')
def create_testsuites(step):
    testsuiteModel = TestsuiteModel()

    for item in step.hashes:
        # must do this or it will freak out the lettuce reporting, because
        # we delete items from this before submitting.
        testsuite = item.copy()

        # get the product id from the passed product name
        product_id = ProductModel().get_resid(testsuite["product name"])[0]

        testsuite["productId"] = product_id

        if testsuite.has_key('product name'):
            del testsuite['product name']

        testsuiteModel.create(testsuite)

@step(u'activate the testsuite with (that name|name "(.*)")')
def activate_testsuite_with_name(step, stored, name):
    testsuiteModel = TestsuiteModel()
    name = testsuiteModel.get_stored_or_store_name(stored, name)

    testsuiteModel.activate(name)


@step(u'testsuite with (that name|name "(.*)") (exists|does not exist)')
def check_testsuite_foo_existence(step, stored, name, existence):
    testsuiteModel = TestsuiteModel()
    name = testsuiteModel.get_stored_or_store_name(stored, name)

    testsuiteModel.verify_existence_on_root(name,
                                            existence = existence)


@step(u'delete the testsuite with (that name|name "(.*)")')
def delete_testsuite_with_name_foo(step, stored, name):
    testsuiteModel = TestsuiteModel()
    name = testsuiteModel.get_stored_or_store_name(stored, name)

    testsuiteModel.delete(name)

@step(u'add the following testcases to the testsuite with (that name|name "(.*)")')
def add_testcases_to_testsuite(step, stored, name):
    testsuiteModel = TestsuiteModel()
    name = testsuiteModel.get_stored_or_store_name(stored, name)

    for tc in step.hashes:
        testsuiteModel.add_testcase(name, tc["name"])


@step(u'add the following testsuites to the testrun with (that name|name "(.*)")')
def add_testsuites_to_testrun(step, stored, testrun_name):
    testrunModel = TestrunModel()
    testrun_name = testrunModel.get_stored_or_store_name(stored, testrun_name)

    for testsuite in step.hashes:
        testrunModel.add_testsuite(testrun_name, testsuite["name"])

@step('create the seed testcycle, testrun and testcases')
def create_seed_testcycle_testcases_testrun(step):
    '''
        Bug in lettuce prevents me from using this technique

    '''



    step.behave_as("""
        Given I create the seed company and product with these names:
            | company name    | product name  |
            | Massive Dynamic | Cortexiphan   |
        When I create a new user with name "Capn Admin"
        and I activate the user with that name
        And I create a new role with name "Approvationalist" with the following permissions:
            | permissionCode               |
            | PERMISSION_TEST_CASE_EDIT    |
            | PERMISSION_TEST_CASE_APPROVE |
        And I add the role with name "Approvationalist" to the user with that name
        when the user with that name creates a new testcase with name "Check the Gizmo"
        and when I add these steps to the testcase with that name:
            | name      | stepNumber | estimatedTimeInMin | instruction    | expectedResult        |
            | Mockery   | 1          | 5                  | Go this way    | They went this way    |
            | Flockery  | 2          | 2                  | Go that way    | They went that way    |
            | Chockery  | 3          | 4                  | Go my way      | They went my way      |
            | Trockery  | 4          | 1                  | Go the highway | They went the highway |
            | Blockery  | 5          | 25                 | Just go away   | They went away        |
        Then when I create a new user with name "Joe Approver"
        and I activate the user with that name
        And I add the role with name "Approvationalist" to the user with that name
        and when the user with name "Joe Approver" approves the testcase with that name
        And when I create the following new testcycles:
            | name          | description               | product name | startDate  | endDate    | communityAuthoringAllowed | communityAccessAllowed |
            | Baroque Cycle | Ahh, the cycle of life... | Cortexiphan  | 2011/02/02 | 2012/02/02 | true                      | true                   |
        and when I create a new testrun with name "Running Man" with testcycle "Baroque Cycle"
    """)




