'''
######################################################################

                     DATA SUBMISSION HELPER FUNCTIONS

######################################################################
These functions generate data to be submitted in POST operations

Created on Oct 21, 2010
@author: camerondawson
'''
import urllib


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

def get_submit_testcase_params(description, name):
    tc = {
          "productid":"1",
          "maxattachmentsizeinmbytes":"10",
          "maxnumberofattachments":"5",
          "name": name,
          "description": description,
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
    return tc


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


def get_submit_user_params(fname, lname):    
    user = {
                "firstname":fname,
                "lastname":lname,
                "email":fname+lname + "@utest.com",
                "screenname":fname+lname,
                "password":fname+lname +"123",
                "companyid":9,
                "communitymember":"false"
    }

    return user

def get_submit_company_params(co_name):
    company = {
                "name": co_name,
                "phone": "617-417-0593",
                "address": "31 lakeside drive",
                "city": "Boston",
                "zip": "01721",
                "url": "http//www.utest.com",
                "countryId": 123
    }
    return company

