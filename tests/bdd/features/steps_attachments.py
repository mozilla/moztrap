'''
Created on Jan 31, 2011

@author: camerondawson
'''

from features.tcm_request_helper import get_testcase_resid, \
    encode_multipart_formdata, do_post
from lettuce import step, world

'''
######################################################################

                     ATTACHMENT STEPS

######################################################################
'''

'''
    Hmmm, this may not work.  May be a special case I need to call explicitly, not
    with the do_post method.
'''


@step(u'upload attachment with filename "(.*)" to test case with name "(.*)"')
def upload_attachment_foo_to_test_case_bar(step, attachment, test_case):
    test_case_id, version = get_testcase_resid(test_case)

    content_type, body = encode_multipart_formdata([], [{'key': attachment,
                                                         'filename': attachment,
                                                         'value': open(world.testfile_dir + attachment, 'rb')}])

    headers = {"Accept": "application/xml",
               "Content-Type":content_type,
               "Content-Length": "%d" % len(body) }

    do_post(world.path_testcases + str(test_case_id) + "/attachments/upload",
            body,
            {"originalVersionId": version})


