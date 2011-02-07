'''
Created on Jan 31, 2011

@author: camerondawson
'''

from lettuce import *
#from nose.tools import *
from step_helper import *

'''
######################################################################

                     ATTACHMENT STEPS

######################################################################
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

    world.conn.request("POST", 
                       add_params(world.path_testcases + test_case_id + "/attachments/upload", 
                                  {"originalVersionId": version}), 
                       body, headers)

    response = world.conn.getresponse()
    verify_status(200, response, "upload attachment with filename")
    

