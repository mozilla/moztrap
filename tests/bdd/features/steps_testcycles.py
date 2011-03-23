'''
Created on Mar 23, 2011

@author: camerondawson
'''
from features.models import TestcycleModel
from features.tcm_data_helper import get_result_status_id, \
    verify_single_item_in_list, ns, jstr
from features.tcm_request_helper import get_resource_identity
from lettuce.decorators import step


@step(u'(that testcycle|the testcycle with name "(.*)") has the following result status summary counts')
def testcycle_has_summary_counts(step, stored_testcycle, testcycle_name):
    testcycleModel = TestcycleModel()

    testcycle = testcycleModel.get_stored_or_store_obj(stored_testcycle, testcycle_name)

    testcycle_id = get_resource_identity(testcycle)[0]

    # get the list of testcases for this testcycle
    summary_list = testcycleModel.get_summary_list(testcycle_id)

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
