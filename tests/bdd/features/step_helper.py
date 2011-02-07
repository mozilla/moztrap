'''
Created on Nov 9, 2010

@author: camerondawson
'''
from lettuce import *
import base64
import copy
import json
import mimetypes
import re
import string
import urllib
#from types import ListType


'''
######################################################################

                     HELPER FUNCTIONS

######################################################################
'''

def get_stored_or_store_name(objtype, stored, name):
    '''
        Help figure out if the test writer wants to use a stored name from a previous step, or if
        the name was passed in explicitly. 
        
        If they refer to a user as 'that name' rather than 'name "foo bar"' then it uses
        the stored one.  Otherwise, the explicit name passed in.  
    '''
    if (stored.strip() == "that name"):
        name = world.names[objtype]
    else:
        world.names[objtype] = name
    return name

def ns(field):
    '''
        Ensures the namespace is added to the beginning of the field name.
        If it already is, don't add it again, though.  How clever.
    '''
    if not re.search(world.ns, field):
        field = world.ns + field
    
    return field

def add_params(uri_path, params = {}):
    '''
        add the param to request JSON responses to the params object
        I'll first add on the URI prefix
        then add in the params
    '''
    newparams = copy.copy(params)
    newparams["_type"] = "json"
    #assert False, urllib.urlencode(params)
    #assert False, params
    
    uri = uri_path + "?" + urllib.urlencode(newparams)
    #if re.search("companies", uri_suffix):
        #assert False, uri
    return uri

def verify_status(exp_status, response, msg):
    '''
        Helper that prints out the error message if something other than what's expected
        is returned.
    '''
    data = response.read()
    eq_(response.status, 200, msg + ": " + str(data))
    return data
    
def eq_(act, exp, msg):
    assert exp == act, "\n\tExp:%r\n\tAct:%r\n%r" % (exp, act, msg)
    
def get_auth_header():
    userid = "admin@utest.com" 
    passwd = "admin"

    auth = 'Basic ' + string.strip(base64.encodestring(userid + ':' + passwd))

    return auth

def get_user_status_id(userStatus):
    statusMap = {"active": 1,
                 "inactive": 2,
                 "disabled": 3}
    return statusMap.get(userStatus)


def search_and_verify_existence(step, uri, search_args, obj_name, existence):
    expect_to_find = (existence.strip() == "exists")
    search_and_verify(step, uri, search_args, obj_name, expect_to_find)

def search_and_verify(step, uri, search_args, obj_name, expect_to_find):
    '''
        This does a search based on the search_args passed in.  So "expect_to_find"
        is really filtered based on those parameters.  
        
        expect_to_find: If True, then we verify based on expecting to find something.
                        If False, this will fail if we get a resultset greater than 0.
    '''
    #arg_value_enc = urllib.quote(arg_value)
    url = add_params(uri, search_args)

    headers = {'Content-Type':'application/json',
               'Authorization': get_auth_header()}
    
    world.conn.request("GET", url, "", headers)
    response = world.conn.getresponse()

    data = verify_status(200, response, uri + " existence")

    if not expect_to_find:
        count = get_count(data, ns(obj_name))
        eq_(count, 0, "expect result size zero")
    else:
        environmentJson = get_single_item(data, ns(obj_name))

        # Verify that the result's values match our search params 
        for k, v in search_args.items():
            eq_(environmentJson.get(ns(k)), v, obj_name + " match")
    


def get_single_item(response_txt, type):
    '''
        Expect the response to be a single item.  If it's more, we assert.
    '''
    type = ns(type)
    pl_type = plural(type)

    try:
        respJson = json.loads(response_txt)
    except ValueError:
        assert False, "Bad JSON: " + str(response_txt)
    except TypeError:
        assert False, "Bad JSON: " + str(response_txt)
    
    item = None
    
    # if this was a search, extract the item from the "searchResult" object
    # in this case, we only care about the first returned item in this list
    sr_field = ns("searchResult")
    if (respJson.__contains__(sr_field)):
        sr = respJson.get(sr_field)

        assert sr[0].__contains__(pl_type), "didn't find expected type: %s in:\n%s" % (pl_type, jstr(sr))
        pl_item = sr[0].get(pl_type)

        assert pl_item.__contains__(type), "didn't find expected type: %s within %s in:\n%s" % (type, pl_type, jstr(sr))
        items = pl_item.get(type)
            
        if (len(items) > 0) and isinstance(items, list):
            item = items[0]
        else:
            item = items
    else:
        item = respJson.get(type)

    assert item != None, "didn't find expected type: " + type + " in:\n" + jstr(respJson)
    return item


def get_first_item(response_txt, type):
    '''
        Expect the response to be a single item or a list.  
        If it's a list, we take the first item.
    '''
    type = ns(type)
    pl_type = plural(type)

    try:
        respJson = json.loads(response_txt)
    except ValueError:
        assert False, "Bad JSON: " + str(response_txt)
    except TypeError:
        assert False, "Bad JSON: " + str(response_txt)
    
    item = None
    
    # if this was a search, extract the item from the "searchResult" object
    # in this case, we only care about the first returned item in this list
    sr_field = ns("searchResult")
    if (respJson.__contains__(sr_field)):
        sr = respJson.get(sr_field)

        assert sr[0].__contains__(pl_type), "didn't find expected type: %s in:\n%s" % (pl_type, jstr(sr))
        pl_item = sr[0].get(pl_type)

        assert pl_item.__contains__(type), "didn't find expected type: %s within %s in:\n%s" % (type, pl_type, jstr(sr))
        items = pl_item.get(type)
            
        if (len(items) > 0) and isinstance(items, list):
            item = items[0]
        else:
            item = items
    else:
        item = respJson.get(type)

    assert item != None, "didn't find expected type: " + type + " in:\n" + jstr(respJson)
    return item
  
  
def get_count(response_txt, type):
    '''
        Expect the response to be a single item or a list.  
        If it's a list, we take the first item.
    '''
    type = ns(type)
    pl_type = plural(type)

    try:
        respJson = json.loads(response_txt)
    except ValueError:
        assert False, "Bad JSON: " + response_txt
    
    count = None
    
    # if this was a search, extract the item from the "searchResult" object
    # in this case, we only care about the first returned item in this list
    sr_field = ns("searchResult")
    if (respJson.__contains__(sr_field)):
        sr = respJson.get(sr_field)

        assert sr[0].__contains__(pl_type), "didn't find expected type: %s in:\n%s" % (pl_type, jstr(sr))
                 
        count = sr[0].get(ns("totalResults"))
            

    assert count != None, "didn't find " + sr_field + " or " + ns("totalResults") + " in:\n" + jstr(respJson)
    return count
      

def get_resp_list(response, type):
    '''
        Expect the response to be a search result containing a list.
        The list may be a list of size 1, though.
    '''

    type = ns(type)
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
    return get_resource_identity("user", add_params(world.path_users, {"firstName": names[0], "lastName": names[1]}))

def get_role_resid(role):
    '''
        Get the resourceIdentity of a role, based on the description of the role
    '''
    return get_resource_identity("role", add_params(world.path_roles, {"description": role}))

def get_product_resid(product):
    '''
        Get the resourceIdentity, based on the name
    '''
    return get_resource_identity("product", add_params(world.path_products, {"name": product}))

def get_environment_resid(environment):
    '''
        Get the resourceIdentity, based on the name
    '''
    return get_resource_identity("environment", add_params(world.path_environments, {"name": environment}))
    

def get_environmenttype_resid(environment):
    '''
        Get the resourceIdentity, based on the name
    '''
    return get_resource_identity("environmenttype", add_params(world.path_environmenttypes, {"name": environment}))
    
def get_environmentgroup_resid(environment):
    '''
        Get the resourceIdentity, based on the name
    '''
    return get_resource_identity("environmentgroup", add_params(world.path_environmentgroups, {"name": environment}))

def get_testcase_resid(testcase):
    '''
        Get the resourceIdentity, based on the name
    '''
    return get_resource_identity("testcase", add_params(world.path_testcases, {"name" : testcase}))

def get_resource_identity(type, uri):
    '''
        type: Something like user or role or permission.  The JSON object type
        uri: The URI stub to make the call
        
        Return the id and version as strings
        
        @TODO: This presumes a list of objects is returned.  So it ONLY returns the resid for
        the first element of the list.  Will almost certainly need a better solution in the future.
        Like a new method "get_resource_identities" which returns a list of ids or something.  
    '''

    headers = {'Content-Type':'application/json',
               'Authorization': get_auth_header()}

    world.conn.request("GET", uri, "", headers)
    response = world.conn.getresponse()
    data = verify_status(200, response, "Response when asking for " + type)
    
    field = ns("resourceIdentity")
    respJson = get_single_item(data, type)
    assert respJson.__contains__(field), "Object doesn't have " + field + ":\n" + jstr(respJson)
    resid = respJson.get(field);
    assert resid.__contains__("@id"), "Result should have @id" + ":\n" + jstr(respJson)
    assert resid.__contains__("@version"), "Result should have @version" + ":\n" + jstr(respJson)
    # we always use this as a string
    return str(resid.get("@id")), str(resid.get("@version")) 


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
              world.ns + "attachment": world.ns + "attachments",
              world.ns + "company": world.ns + "companies",
              world.ns + "environment": world.ns + "environments",
              world.ns + "environmenttype": world.ns + "environmenttypes",
              world.ns + "permission":world.ns + "permissions",
              world.ns + "product":world.ns + "products",
              world.ns + "role":world.ns + "roles",
              world.ns + "testcase": world.ns + "testcases",
              world.ns + "testcycle":world.ns + "testcycles",
              world.ns + "testplan":world.ns + "testplans",
              world.ns + "testrun":world.ns + "testruns",
              world.ns + "testsuite":world.ns + "testsuites",
              world.ns + "user": world.ns + "users"
              }

    plural_type = pl_map.get(type)
    assert plural_type, "Couldn't find plural of %s" % (type, )
    return plural_type

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


