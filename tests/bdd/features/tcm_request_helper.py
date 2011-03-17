'''
Created on Mar 8, 2011

@author: camerondawson
'''
from features.tcm_data_helper import eq_, get_user_password, record_api_for_step, \
    jstr, json_to_obj, as_arrayof, plural, json_pretty
from lettuce.terrain import world
from tcm_data_helper import ns
import base64
import copy
import mimetypes
import string
import urllib

def get_auth_header(userid = "admin@utest.com", passwd = "admin"):
    auth = 'Basic ' + string.strip(base64.encodestring(userid + ':' + passwd))

    return auth

def get_form_headers(auth_header = get_auth_header()):
    return {'Authorization': auth_header,
            'content-type': "application/x-www-form-urlencoded"}

def get_json_headers(auth_header = get_auth_header()):
    return {'Authorization': auth_header,
            'Content-Type':'application/json'}
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
    eq_(response.status, exp_status, msg + ": " + str(data))
    return data

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

def log_user_in(name):
    headers = get_json_headers(get_auth_header_user_name(name))
    # log the user in

    return do_put_for_cookie(world.path_users + "login", "", headers)






def do_get(uri, params = {}, headers = get_json_headers(), exp_status = 200):

    record_api_for_step("GET", uri)

    world.conn.request("GET", add_params(uri, params), "", headers)
    response = world.conn.getresponse()
    return verify_status(exp_status, response, str(uri))

def do_put_for_cookie(uri, body, headers = get_form_headers()):
    '''
        usually we don't care about the returned headers,  but in
        the case of login, for instance, we need the cookie it returns
    '''
    method = "PUT"

    record_api_for_step(method, uri)

    world.conn.request(method, add_params(uri),
                       urllib.urlencode(body, doseq=True),
                       headers)
    response = world.conn.getresponse()

    # stolen from Carl Meyer's code
    # Work around httplib2's broken multiple-header handling
    # http://code.google.com/p/httplib2/issues/detail?id=90
    # This will break if a cookie value contains commas.
    cookies = [c.split(";")[0].strip() for c in
               response.getheader("set-cookie").split(",")]
    auth_cookie = [c for c in cookies if c.startswith("USERTOKEN=")][0]



    data = verify_status(200, response, "%s %s:\n%s" % (method, uri, body))
    return data, auth_cookie

def do_put(uri, body, headers = get_form_headers()):
    return do_request("PUT", uri, body = body, headers = headers)

def do_post(uri, body, params = {}, headers = get_form_headers()):
    return do_request("POST", uri, body = body, headers = headers)

def do_delete(uri, params, headers = get_form_headers()):
    return do_request("DELETE", uri, params = params, headers = headers)

def do_request(method, uri, params = {}, body = {}, headers = get_form_headers(), exp_status = 200):
    '''
        do the request
    '''

    record_api_for_step(method, uri)

    world.conn.request(method, add_params(uri, params),
                       urllib.urlencode(body, doseq=True),
                       headers)
    response = world.conn.getresponse()

    return verify_status(exp_status, response, "%s %s:\n%s" % (method, uri, body))

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

    resp_list = get_list_from_search(obj_name, uri, params = search_args)

    if not expect_to_find:
        eq_(len(resp_list), 0, "expect result size zero:\n" + jstr(resp_list))
    else:
        # we want to verify just ONE of the items returned.  Indeed, we likely
        # expect only one.  So we pick the first item returned
        item = resp_list[0]

        # Verify that the result's values match our search params
        for k, v in search_args.items():
            eq_(item.get(ns(k)), v, obj_name + " match")




'''
######################################################################

                     RESID FUNCTIONS

######################################################################
'''
def get_user_resid(name):
    '''
        name: Split into 2 parts at the space.  Only the first two parts are used.  Must have at least 2 parts.
    '''
    names = name.split()
    return search_for_resid("user", world.path_users, {"firstName": names[0], "lastName": names[1]})

def get_role_resid(role):
    '''
        Get the resourceIdentity of a role, based on the description of the role
    '''
    return search_for_resid("role", world.path_roles, {"name": role})

def get_product_resid(product):
    '''
        Get the resourceIdentity, based on the name
    '''
    return search_for_resid("product", world.path_products, {"name": product})

def get_seed_product_id():
    return  get_product_resid(world.seed_product["name"])[0]

def get_company_resid(company):
    return search_for_resid("company", world.path_companies, {"name": company})

def get_seed_company_id():
    return get_company_resid(world.seed_company["name"])[0]

def get_country_resid(country):
    return search_for_resid("country", world.path_countries, {"name": country})

def get_environment_resid(environment):
    return search_for_resid("environment", world.path_environments, {"name": environment})

def get_environmenttype_resid(environment):
    return search_for_resid("environmenttype", world.path_environmenttypes, {"name": environment})

def get_environmentgroup_resid(environment):
    return search_for_resid("environmentgroup", world.path_environmentgroups, {"name": environment})

def get_testcase_resid(name):
    return search_for_resid("testcase", world.path_testcases, {"name" : name})

def get_testsuite_resid(name):
    return search_for_resid("testsuite", world.path_testsuites, {"name" : name})

def get_testcycle_resid(name):
    return search_for_resid("testcycle", world.path_testcycles, {"name": name})

def get_testrun_resid(name):
    return search_for_resid("testrun", world.path_testruns, {"name": name})

def get_tag_resid(tag):
    return search_for_resid("tag", world.path_tags, {"tag": tag})

def search_for_resid(tcm_type, uri, params = {}):
    '''
        tcm_type: Something like user or role or permission.
        uri: The URI stub to make the call

        Return the id and version as strings

        @TODO: This presumes a list of objects is returned.  So it ONLY returns the resid for
        the first element of the list.  Will almost certainly need a better solution in the future.
        Like a new method "get_resource_identities" which returns a list of ids or something.
    '''

    item = get_single_item_from_search(tcm_type, uri, params = params)
    assert item != None, "%s not found in search with these params: %s" % (tcm_type, jstr(params))
    return get_resource_identity(item)

def get_resource_identity(tcm_obj):

    try:
        resid = int(tcm_obj[ns("resourceIdentity")]["@id"])
        version = tcm_obj[ns("resourceIdentity")]["@version"]
        return resid, version
    except KeyError:
        assert False, "didn't find expected tcm_type:  %s -- %s or %s in:\n%s" % (ns("resourceIdentity"),
                                                                     "@id",
                                                                     "@version",
                                                                     jstr(tcm_obj))


def get_testcase_latestversion_resid(testcase_id):
    # now get the latest version for that testcase id

    latestversion_uri = world.path_testcases + "%s/latestversion/" % testcase_id

    testcaseversion = get_single_item_from_endpoint("testcaseversion", latestversion_uri)
    return get_resource_identity(testcaseversion)

def get_stored_or_store_obj(tcm_type, stored, name):
    '''
        If stored is not None and has the word "that" in it, then we try to use the last stored object
        of that type.  This can be tricky, because that last stored one might not have the latest verison id.
        Some step code may need to refetch the latest version.  Or perhaps we should re-fetch the latest
        version here?

        If stored IS None, then we do a search for the object of that type with that name.  For type of "users"
        we have to split the name to first and last.  Sucky special case.
    '''
    if stored == None:
        # search for the object with that name
        if tcm_type == "user":
            names = name.split()
            params = {"firstName": names[0], "lastName": names[1]}
        else:
            params = {"name": name}
        tcm_obj = get_single_item_from_search(tcm_type, tcmpath(tcm_type), params)
        store_latest_of_type(tcm_type, tcm_obj)
    else:
        # returned the stored object
        # DO WE RE-FETCH IT TO GET THE LATEST VERSION?
        tcm_obj = get_latest_of_type(tcm_type)
        tcm_obj = get_single_item_from_endpoint(tcm_type, tcmpath(tcm_type) + str(get_resource_identity(tcm_obj)[0]))
        return tcm_obj

def tcmpath(tcm_type):
    '''
        The URI path for a given tcm object type.  Shortcut to make the code cleaner.
    '''
    if not tcm_type.endswith('s'):
        # needs to be plural
        return world.path_map[plural(tcm_type)]
    return world.path_map[tcm_type]
'''
######################################################################

                     LIST FUNCTIONS

######################################################################
'''


def get_list_from_search(tcm_type, uri, params = {}, headers = get_json_headers()):
    '''
        This will always return an array.  May have many, one or no items in it
        it goes into the "searchResult" tcm_type of response
    '''
    response_txt = do_get(uri, params, headers)

    sr_field = ns("searchResult")
    tcm_type = ns(tcm_type)
    pl_type = plural(tcm_type)

    try:
        sr = json_to_obj(response_txt)[sr_field][0]
        if (sr[ns("totalResults")] > 0):
            items = sr[pl_type][tcm_type]
            if (not isinstance(items, list)):
                items = [items]
        else:
            items = []

        return items
    except (KeyError, TypeError) as err:
        assert False, \
            "%s\nDidn't find [%s][0][%s][%s] in\n%s" % \
            (str(err),
             sr_field,
             pl_type,
             ns(tcm_type),
             json_pretty(response_txt))

def get_single_item_from_search(tcm_type, uri, params = {}, headers = get_json_headers()):
    '''
        This will always return a single item or None type.  May have many responses, so throw an
        error if there is more than one.
        It goes into the "searchResult" tcm_type of response

        Yeah, it's inefficient to create a list, then potentially return the first item as NOT a list.
        But this makes the coding easier and more uniform, so I chose to do that.
    '''
    list = get_list_from_search(tcm_type, uri, params = params, headers = headers)

    # if the last attempt to get something returned None, we want to persist that in the last_id,
    # otherwise we may think we're referencing the LAST one, but we'd be getting the one from before
    if len(list) == 0:
        store_latest_of_type(tcm_type, None)
        return None
    assert len(list) < 2,\
        "More than one object returned from search.  Don't know which one to return:\n%s"\
        % jstr(list)

    item = list[0]
    store_latest_of_type(tcm_type, item)
    return item


def get_list_from_endpoint(tcm_type, uri, headers = get_json_headers()):
    '''
        This hits an endpoint.  It goes into the ArrayOfXXX tcm_type of response
    '''
    response_txt = do_get(uri, headers = headers)

    try:
        array_of_type = json_to_obj(response_txt)[ns(as_arrayof(tcm_type))][0]
        if (len(array_of_type) > 1):
            items = array_of_type[ns(tcm_type)]
            if (not isinstance(items, list)):
                items = [items]
        else:
            items = []

        return items
    except (KeyError, TypeError) as err:
        assert False, \
            "%s\nDidn't find [%s][0][%s] in\n%s" % \
            (str(err),
             ns(as_arrayof(tcm_type)),
             ns(tcm_type),
             json_pretty(response_txt))

def get_single_item_from_endpoint(tcm_type, uri, headers = get_json_headers()):
    '''
        This hits an endpoint.  No searchResult or ArrayOfXXXX part here
    '''

    response_txt = do_get(uri, headers = headers)

    try:
        item = json_to_obj(response_txt)[ns(tcm_type)][0]
        store_latest_of_type(tcm_type, item)
        return item

    except KeyError:
        assert False, "%s\nDidn't find %s in %s" % (str(KeyError), ns(tcm_type), response_txt)


# simple accessors that can be changed if I change where I store these things.
def store_latest_of_type(tcm_type, tcm_obj):
    world.latest_of_type[tcm_type] = tcm_obj

def get_latest_of_type(tcm_type):
    return world.latest_of_type[tcm_type]





'''
    UPLOAD FILES
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



