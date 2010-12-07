'''
Created on Nov 9, 2010

@author: camerondawson
'''
from lettuce import *
from numpy.ma.testutils import *
from types import ListType
import json
import urllib
import mimetypes

'''
######################################################################

                     HELPER FUNCTIONS

######################################################################
'''

def check_existence(step, uri, arg_name, arg_value, obj_name, existence):
    arg_value_enc = urllib.quote(arg_value)
    world.conn.request("GET", "/api/v1/" + uri + "?" + arg_name + "=" + arg_value_enc)
    response = world.conn.getresponse()

    if existence.strip() == "does not exist":
        assert_equal(response.status, 404, uri + " existence")
    else:
        assert_equal(response.status, 200, uri + " existence")

        environmentJson = get_single_item(response, obj_name)
        assert_equal(environmentJson.get(arg_name), arg_value, obj_name + " name match")
    


def get_single_item(response, type):
    '''
        Expect the response to be a single item or a list.  
        If it's a list, we take the first item.
    '''

    respJson = json.loads(response.read())

    item = None
    
    # if this was a search, extract the item from the "searchResult" object
    # in this case, we only care about the first returned item in this list
    if (respJson.__contains__("searchResult")):
        sr = respJson.get("searchResult")
        assert sr.__contains__(plural(type)), "didn't find expected type: " + plural(type) + " in:\n" + jstr(sr)
                 
        items = sr.get(plural(type)).get(type)
            
        if (len(items) > 0) and isinstance(items, list):
            item = items[0]
        else:
            item = items
    else:
        item = respJson.get(type)

    assert item != None, "didn't find expected type: " + type + " in:\n" + jstr(respJson)
    return item

def get_resp_list(response, type):
    '''
        Expect the response to be a search result containing a list.
        The list may be a list of size 1, though.
    '''
    respJson = json.loads(response.read())

    resp_list = []
    
    # if this was a search, extract the item from the "searchResult" object
    # in this case, we only care about the first returned item in this list
    if (respJson.__contains__("searchResult")):
        sr = respJson.get("searchResult")
        assert sr.__contains__(plural(type)), "didn't find expected type: " + plural(type) + " in:\n" + jstr(sr) 
        items = sr.get(plural(type)).get(type)
        if isinstance(items, list):
            resp_list = items
        else:
            resp_list.append(items)

    return resp_list
    

def get_user_resid(name):
    ''' 
        name: Split into 2 parts at the space.  Only the first two parts are used.  Must have at least 2 parts.
    '''
    names = name.split()
    return get_resource_identity("user", "/api/v1/users?firstName=" + names[0] + "&lastName=" + names[1])

def get_role_resid(role):
    '''
        Get the resourceIdentity of a role, based on the description of the role
    '''
    return get_resource_identity("role", "/api/v1/roles?description=" + role)

def get_product_resid(product):
    '''
        Get the resourceIdentity of a role, based on the description of the role
    '''
    return get_resource_identity("product", "/api/v1/products?name=" + urllib.quote(product))

def get_environment_resid(environment):
    '''
        Get the resourceIdentity of a role, based on the description of the role
    '''
    return get_resource_identity("environment", "/api/v1/environments?name=" + urllib.quote(environment))

def get_test_case_resid(test_case):
    '''
        Get the resourceIdentity of a role, based on the description of the role
    '''
    return get_resource_identity("testcase", "/api/v1/testcases?name=" + urllib.quote(test_case))

def get_resource_identity(type, uri):
    '''
        type: Something like user or role or permission.  The JSON object type
        uri: The URI stub to make the call
        
        Return the id as a string.
        
        @TODO: This presumes a list of objects is returned.  So it ONLY returns the resid for
        the first element of the list.  Will almost certainly need a better solution in the future.
        Like a new method "get_resource_identities" which returns a list of ids or something.  
    '''
    world.conn.request("GET", uri)
    response = world.conn.getresponse()
    assert_equal(response.status, 200, "Response when asking for " + type)
    
    field = "resourceIdentity"
    respJson = get_single_item(response, type)
    assert respJson.__contains__(field), "Object doesn't have " + field + ":\n" + jstr(respJson)
    # we always use this as a string
    return str(respJson.get(field).get("id"))


def find_ordered_response(type, field, first, second, obj_list):
    # now walk through the expected items and check the response
    # to see that it is represented in the right order
    foundFirst = False
    foundSecond = False
    
    for act_item in obj_list:
        act = act_item.get(field)
        if (first == act):
            foundFirst = True
            assert foundSecond == False, "found %(second) before %(first)" % {'second':second, 'first':first}
        if (second == act):
            foundSecond = True
            assert foundFirst == True, "found %(second) before %(first)" % {'second':second, 'first':first}

    # since it's possible to drop through here without finding one or the other, we have to check that 
    # both were actually found.
    assert foundFirst == True, "First was found"
    assert foundSecond == True, "Second was found"
    
def plural(type):
    pl_map = {
              "attachment": "attachments",
              "company": "companies",
              "environment": "environments",
              "environmenttype": "environmenttypes",
              "permission":"permissions",
              "product":"products",
              "role":"roles",
              "testcase": "testcases",
              "testcycle":"testcycles",
              "testplan":"testplans",
              "testrun":"testruns",
              "testsuite":"testsuites",
              "user": "users"
              }

    return pl_map.get(type)

def jstr(obj):
    return json.dumps(obj, sort_keys=True, indent=4)

'''
    Upload files.
'''
def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


