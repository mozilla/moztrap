'''
Created on Nov 9, 2010

@author: camerondawson
'''
from lettuce.terrain import world
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
    return get_stored_or_store_field("name", objtype, stored, name)

def get_stored_or_store_field(field_name, objtype, stored, name):
    '''
        Help figure out if the test writer wants to use a stored name from a previous step, or if
        the name was passed in explicitly. 
        
        If they refer to a user as 'that name' rather than 'name "foo bar"' then it uses
        the stored one.  Otherwise, the explicit name passed in.  
    '''
    if (stored.strip() == "that " + field_name):
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
    
def get_auth_header(userid = "admin@utest.com", passwd = "admin"):

    auth = 'Basic ' + string.strip(base64.encodestring(userid + ':' + passwd))

    return auth

def get_auth_header_user_name(user_name):
    names = user_name.split()
    user_list = get_list_from_search("user",
                                     world.path_users,
                                     {"firstName": names[0], "lastName": names[1]})
    try:
        useremail = user_list[0][ns("email")]
        userpw = get_user_password(user_name)
    except KeyError:
        assert False, "%s\nDidn't find field in %s" % (str(KeyError), user_list)

    return get_auth_header(useremail, userpw)

# for simplicity, we just always use the same algorithm for passwords
def get_user_password(name):
    names = name.split()
    return "%s%s123" % (names[0], names[1])

def get_list_from_search(type, uri, params = {}, auth_header = get_auth_header()):
    '''
        This will always return an array.  May have many, one or no items in it
        it goes into the "searchResult" type of response
    '''
    response_txt = do_get(uri, params)
    
    return get_search_result_list(response_txt, type)

def get_list_from_endpoint(type, uri, auth_header = get_auth_header()):
    '''
        This hits an endpoint.  It goes into the ArrayOfXXX type of response
    '''
    response_txt = do_get(uri)

    return get_list_of_type(type, response_txt)

def get_single_item_from_endpoint(type, uri, auth_header = get_auth_header()):
    '''
        This hits an endpoint.  It goes into the ArrayOfXXX type of response
    '''
    
    response_txt = do_get(uri)
    
    try:
        return json_to_obj(response_txt)[ns(type)][0]
    except KeyError:
        assert False, "%s\nDidn't find %s in %s" % (str(KeyError), ns(type),response_txt)


def do_get(uri, params = {}, auth_header = get_auth_header()):

    headers = {'Content-Type':'application/json',
               'Authorization': auth_header}

    record_api_for_step("GET", uri)
    
    world.conn.request("GET", add_params(uri, params), "", headers)
    response = world.conn.getresponse()
    return verify_status(200, response, str(uri))

def do_post(uri, body, params = {}, auth_header = get_auth_header()):
    return do_request("POST", uri, body = body, auth_header = auth_header)

def do_put(uri, body, auth_header = get_auth_header()):
    return do_request("PUT", uri, body = body, auth_header = auth_header)

def do_delete(uri, params, auth_header = get_auth_header()):
    return do_request("DELETE", uri, params = params, auth_header = auth_header)

def do_request(method, uri, params = {}, body = {}, auth_header = get_auth_header()):
    ''' 
        do the request
    '''
    headers = {'Authorization': auth_header,
               'content-type': "application/x-www-form-urlencoded"}

    record_api_for_step(method, uri)
    
    world.conn.request(method, add_params(uri, params), 
                       urllib.urlencode(body, doseq=True), 
                       headers)
    response = world.conn.getresponse()

    return verify_status(200, response, "%s %s:\n%s" % (method, uri, body))



def record_api_for_step(method, uri):
    '''
        This should look like:
        {"Given I create a user": 
            {"/users/foo": 
                ["POST", "GET"]
            }
        }
    '''
    # if the uri has a number/id in it, we want to replace that with "{id}" so we
    # don't get repeats for different ids.
    
    if uri.startswith(world.api_prefix):
        uri = uri[len(world.api_prefix):]
    
    uri_parts = uri.strip().split("/")
    for index, item in enumerate(uri_parts):
        try:
            int(item)
            uri_parts[index] = "{id}"
        except ValueError:
            # not a number, that's ok
            pass
    
    uri = '/'.join(uri_parts)
    
    
    methods = world.apis_called.setdefault(uri, set())
    methods.add(method)
    
def search_and_verify_existence(uri, search_args, obj_name, existence):
    expect_to_find = (existence.strip() == "exists")
    search_and_verify(uri, search_args, obj_name, expect_to_find)

def search_and_verify(uri, search_args, obj_name, expect_to_find):
    '''
        This does a search based on the search_args passed in.  So "expect_to_find"
        is really filtered based on those parameters.  
        
        expect_to_find: If True, then we verify based on expecting to find something.
                        If False, this will fail if we get a resultset greater than 0.
    '''
    
    data = do_get(uri, search_args)
    
    if not expect_to_find:
        count = get_count(data, ns(obj_name))
        eq_(count, 0, "expect result size zero:\n" + data)
    else:
        environmentJson = get_single_item(data, ns(obj_name))

        # Verify that the result's values match our search params 
        for k, v in search_args.items():
            eq_(environmentJson.get(ns(k)), v, obj_name + " match")

def search_and_verify_array(uri, search_args, obj_name, expect_to_find):
    '''
        This does a search based on the search_args passed in.  So "expect_to_find"
        is really filtered based on those parameters.  
        
        expect_to_find: If True, then we verify based on expecting to find something.
                        If False, this will fail if we get a resultset greater than 0.
    '''
    data = do_get(uri, search_args)

    if not expect_to_find:
        count = get_count(data, ns(obj_name))
        eq_(count, 0, "expect result size zero:\n" + data)
    else:
        environmentJson = get_array_item(data, obj_name)

        # Verify that the result's values match our search params 
        for k, v in search_args.items():
            eq_(environmentJson.get(ns(k)), v, obj_name + " match")



















##########################
# THESE METHODS MAY NEED CLEANUP
##########################


def get_user_status_id(userStatus):
    statusMap = {"active": 1,
                 "inactive": 2,
                 "disabled": 3}
    return statusMap.get(userStatus)



def get_resid_from_creation_response(response_txt, type):
    '''
        Expect the response to be a single item.  If it's more, we assert.
    '''
    type = ns(type)

    respJson = json_to_obj(response_txt)
    
    try:
        assert respJson.__contains__(type), "didn't find expected type: %s in:\n%s" % (type, jstr(respJson))
        item = respJson.get(type)

    except KeyError:
        assert False, "Key Error in\n" + jstr(respJson)
    return item

    
    
def get_single_item(response_txt, type):
    '''
        Expect the response to be a single item.  If it's more, we assert.
    '''
    type = ns(type)
    pl_type = plural(type)

    respJson = json_to_obj(response_txt)
    
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

def get_search_result_list(response_txt, type):
    '''
        return the array of this type that's within the search result
    '''
    type = ns(type)
    pl_type = plural(type)

    respJson = json_to_obj(response_txt)
    
    sr_field = ns("searchResult")
    
    assert respJson.__contains__(sr_field), "didn't find expected type: %s in:\n%s" % (sr_field, jstr(respJson))        
    sr = respJson.get(sr_field)

    assert sr[0].__contains__(pl_type), "didn't find expected type: %s in:\n%s" % (pl_type, jstr(sr))
    pl_item = sr[0].get(pl_type)

    assert pl_item.__contains__(type), "didn't find expected type: %s within %s in:\n%s" % (type, pl_type, jstr(sr))
    items = pl_item.get(type)
            
    if (isinstance(items, list)):
        return items
    else:
        return [items]

def get_array_item(response_txt, type):
    '''
        Expect the response to be a single item.  If it's more, we assert.
    '''
    array_type = as_arrayof(type)
    ns_type = ns(type)

    try:
        respJson = json.loads(response_txt)
    except ValueError:
        assert False, "Bad JSON: " + str(response_txt)
    except TypeError:
        assert False, "Bad JSON: " + str(response_txt)
    
    item = None
    

    assert respJson.__contains__(array_type), "didn't find expected type: %s in:\n%s" % (array_type, jstr(respJson))
    objarray = respJson.get(array_type)

    arr_item = objarray[0]
    assert arr_item.__contains__(ns_type), "didn't find expected type: %s within %s in:\n%s" % (ns_type, array_type, jstr(respJson))
    items = arr_item.get(ns_type)
            
    if (len(items) > 0) and isinstance(items, list):
        item = items[0]
    else:
        item = items

    assert item != None, "didn't find expected type: " + ns_type + " in:\n" + jstr(respJson)
    return item

def get_list_of_type(type, response_txt):
    respJson = json_to_obj(response_txt)
    
    try:
        item = respJson[ns(as_arrayof(type))][0][ns(type)]
    except KeyError:
        assert False, "didn't find expected type:  %s -- %s in:\n%s" % (ns(as_arrayof(type)),
                                                                     ns(type),
                                                                     jstr(respJson))

    # If there is only one, this may not come back as a list.  But I don't want to handle
    # that case everywhere, so we guarantee this is a list
    
    if isinstance(item, list):
        return item
    else:
        return [item]


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
      

#def get_resp_list(response, type):
#    '''
#        Expect the response to be a search result containing a list.
#        The list may be a list of size 1, though.
#    '''
#
#    type = ns(type)
#    respJson = json.loads(response.read())
#    resp_list = []
#    
#    # if this was a search, extract the item from the "searchResult" object
#    # in this case, we only care about the first returned item in this list
#    if (respJson.__contains__("searchResult")):
#        sr = respJson.get("searchResult")
#        assert sr.__contains__(plural(type)), "didn't find expected type: " + plural(type) + " in:\n" + jstr(sr) 
#        items = sr.get(plural(type)).get(type)
#        if isinstance(items, list):
#            resp_list = items
#        else:
#            resp_list.append(items)
#
#    return resp_list

def get_user_resid(name):
    ''' 
        name: Split into 2 parts at the space.  Only the first two parts are used.  Must have at least 2 parts.
    '''
    names = name.split()
    return get_resource_identity("user", world.path_users, {"firstName": names[0], "lastName": names[1]})

def get_role_resid(role):
    '''
        Get the resourceIdentity of a role, based on the description of the role
    '''
    return get_resource_identity("role", world.path_roles, {"name": role})

def get_product_resid(product):
    '''
        Get the resourceIdentity, based on the name
    '''
    return get_resource_identity("product", world.path_products, {"name": product})

def get_seed_product_id():
    return  get_product_resid(world.seed_product["name"])[0]

def get_company_resid(product):
    return get_resource_identity("company", world.path_companies, {"name": product})

def get_seed_company_id():
    return get_company_resid(world.seed_company["name"])[0]

def get_country_resid(country):
    return get_resource_identity("country", world.path_countries, {"name": country})

def get_environment_resid(environment):
    return get_resource_identity("environment", world.path_environments, {"name": environment})
    
def get_environmenttype_resid(environment):
    return get_resource_identity("environmenttype", world.path_environmenttypes, {"name": environment})
    
def get_environmentgroup_resid(environment):
    return get_resource_identity("environmentgroup", world.path_environmentgroups, {"name": environment})

def get_testcase_resid(name):
    return get_resource_identity("testcase", world.path_testcases, {"name" : name})

def get_testsuite_resid(name):
    return get_resource_identity("testsuite", world.path_testsuites, {"name" : name})

def get_testcycle_resid(name):
    return get_resource_identity("testcycle", world.path_testcycles, {"name": name})

def get_testrun_resid(name):
    return get_resource_identity("testrun", world.path_testruns, {"name": name})
    
def get_tag_resid(tag):
    return get_resource_identity("tag", world.path_tags, {"tag": tag})

def get_resource_identity(type, uri, params):
    '''
        type: Something like user or role or permission.
        uri: The URI stub to make the call
        
        Return the id and version as strings
        
        @TODO: This presumes a list of objects is returned.  So it ONLY returns the resid for
        the first element of the list.  Will almost certainly need a better solution in the future.
        Like a new method "get_resource_identities" which returns a list of ids or something.  
    '''

    data = do_get(uri, params)

#    headers = {'Content-Type':'application/json',
#               'Authorization': get_auth_header()}
#
#    world.conn.request("GET", uri, "", headers)
#    response = world.conn.getresponse()
#    data = verify_status(200, response, "Response when asking for " + type)
    
    field = ns("resourceIdentity")
    respJson = get_single_item(data, type)
    assert respJson.__contains__(field), "Object doesn't have " + field + ":\n" + jstr(respJson)
    resid = respJson.get(field);
    assert resid.__contains__("@id"), "Result should have @id" + ":\n" + jstr(respJson)
    assert resid.__contains__("@version"), "Result should have @version" + ":\n" + jstr(respJson)
    # we always use this as a string
    return str(resid.get("@id")), str(resid.get("@version")) 

def get_testcase_latestversion_id(testcase_id):
    # now get the latest version for that testcase id
    
    latestversion_uri = world.path_testcases + testcase_id + "/latestversion/"

    response_txt = do_get(latestversion_uri)
    respJson = json_to_obj(response_txt)

    type = ns("testcaseversion")
    assert respJson.__contains__(type), "didn't find expected type: %s in:\n%s" % (type, jstr(respJson))
    tcv = respJson[type][0]

    field = ns("resourceIdentity")
    assert tcv.__contains__(field), "didn't find expected type: %s in:\n%s" % (field, jstr(tcv))
    resid = tcv[field]
    
    assert resid.__contains__("@id"), "didn't find expected type: %s in:\n%s" % ("@id", jstr(resid))
    return resid["@id"]
    
    
def check_first_before_second(field, first, second, obj_list):

    first_idx = [i for i, x in enumerate(obj_list) if x[ns(field)] == first]
    second_idx = [i for i, x in enumerate(obj_list) if x[ns(field)] == second]
    assert first_idx < second_idx, "Expected %s before %s in %s" % (first, second, 
                                                                    jstr(obj_list))
    
    
def plural(type):
    
    if (type == ns("company")):
        plural_type = ns("companies")
    else:
        plural_type = type + "s"   

    return plural_type

def as_arrayof(type):
    return ns("ArrayOf" + str.capitalize(type))
    
def jstr(obj):
    return json.dumps(obj, sort_keys=True, indent=4)

def json_to_obj(response_txt):
    try:
        respJson = json.loads(response_txt)
    except ValueError:
        assert False, "Bad JSON: " + str(response_txt)
    except TypeError:
        assert False, "Bad JSON: " + str(response_txt)
    return respJson

def json_pretty(response_txt):
    return jstr(json_to_obj(response_txt))

def get_POST_headers():
    return {'Authorization': get_auth_header(),
            'content-type': "application/x-www-form-urlencoded"}
def get_GET_headers():
    return {'Content-Type':'application/json',
            'Authorization': get_auth_header()}


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


