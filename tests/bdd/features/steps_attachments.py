'''
Created on Jan 31, 2011

@author: camerondawson
'''

from features.models import TestcaseModel
from lettuce import step

'''
######################################################################

                     ATTACHMENT STEPS

######################################################################
'''

'''
    Hmmm, this may not work.  May be a special case I need to call explicitly, not
    with the do_post method.
'''


@step(u'upload attachment with filename "(.*)" to (that testcase|the testcase with name "(.*)")')
def upload_attachment_foo_to_test_case_bar(step, filename, stored, name):
    testcaseModel = TestcaseModel()
    testcase = testcaseModel.get_stored_or_store_obj(stored, name)
    testcaseModel.upload_attachment(filename, testcase)



