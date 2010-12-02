'''
######################################################################

                     DATA SUBMISSION HELPER FUNCTIONS

######################################################################
These functions generate data to be submitted in POST operations

Created on Oct 21, 2010
@author: camerondawson
'''
import urllib



def get_submit_user(fname, lname):    
    user = """
        {
            "user":{
                "firstname":"%(fname)s",
                "lastname":"%(lname)s",
                "email":"%(fname)s%(lname)s@utest.com",
                "loginname":"%(fname)s%(lname)s",
                "password":"%(fname)s%(lname)s123",
                "companyid":1,
                "communitymember":"false"
            }
        }
    """ % {'fname': fname, 'lname': lname}

    return urllib.quote(user)

def get_submit_role(rolename):
    user = """
        {
            "role":{
                "description":"%(rolename)s"
            }
        }
    """ % {'rolename': rolename}
    return urllib.quote(user)
    
def get_submit_permission(permission_name):
    perm = """
        {
            "permission":{
                "description":"%(permission_name)s"
            }
        }
    """ % {'permission_name': permission_name}

    return urllib.quote(perm)

def get_submit_test_case(name):
    tc = """
        {
            "testcase":{
                "productid":"1",
                "maxattachmentsizeinmbytes":"10",
                "maxnumberofattachments":"5",
                "name": "%(name)s",
                "description":"Generated test case",
                "testcasesteps":{
                    "testcasestep":{
                        "stepnumber":"1",
                        "name":"login name missing ",
                        "instruction":"don't provide login name",
                        "expectedresult":"validation message should appear",
                        "estimatedtimeinmin":"1"
                    }
                }
            }
        }
    """ % {'name': name}
    return urllib.quote(tc)

def get_submit_company(co_name):
    company = """
        {
            "company":{
                "name": "%(co_name)s",
                "phone": "617-417-0593",
                "address": "31 lakeside drive",
                "city": "Boston",
                "zip": "01721",
                "companyUrl": "http//www.utest.com",
                "resourceIdentity": "5",
                "timeline": "bleh"
            }
        }""" % {'co_name': co_name}
    return urllib.quote(company)


def get_submit_environment(env_name):
    environment = """
        {
            "environment": {
                    "name": "%(env_name)s",
                    "localeCode": "en_US",
                    "sortOrder": "0",
                    "environmentTypeId": "1",
                    "resourceIdentity": "...",
                    "timeline": "..."
            }
        }""" % {'env_name': env_name}
    return urllib.quote(environment)


def get_submit_environment_type(envtype_name):
    envtype = """
        {
            "environmentType": {
                "name": "%(envtype_name)s",
                "localeCode": "en_US",
                "sortOrder": "0",
                "resourceIdentity": "010",
                "timeline": "..."
            }
        }""" % {'envtype_name': envtype_name}
    return urllib.quote(envtype)



