'''
Created on Mar 8, 2011

@author: camerondawson
'''
from features.tcm_data_helper import eq_, record_api_for_step, jstr
from lettuce.terrain import world
from tcm_data_helper import ns
import base64
import mimetypes
import string
import urllib

def get_auth_header(userid = "admin@utest.com", passwd = "admin"):
    auth = 'Basic ' + string.strip(base64.encodestring(userid + ':' + passwd))

    return auth

def get_form_headers(auth_header = get_auth_header()):
    return {'Authorization': auth_header,
            'Content-Type': "application/x-www-form-urlencoded"}

def get_json_headers(auth_header = get_auth_header()):
    return {'Authorization': auth_header,
            'Content-Type':'application/json'}

def get_xml_headers(auth_header = get_auth_header()):
    return {'Authorization': auth_header,
            'Content-Type':'application/xml'}

def add_params(uri_path, params = {}):
    '''
        add the param to request JSON responses to the params object
        I'll first add on the URI prefix
        then add in the params
    '''
    newparams = params.copy()
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
    eq_(response.status, exp_status, "URI: %s/n%s" % (msg, str(data)))
    return data

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


'''
######################################################################

                     REQUEST FUNCTIONS

######################################################################
'''


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

def do_request(method, uri, params = {}, body = None, headers = get_form_headers(), exp_status = 200):
    '''
        do the request
    '''

    record_api_for_step(method, uri)

    if body == None:
#        del headers["Content-Type"]
        world.conn.request(method, add_params(uri, params), None, headers)
    else:
        encoded_body = urllib.urlencode(body, doseq=True)
        world.conn.request(method, add_params(uri, params),
                           encoded_body,
                           headers)

    response = world.conn.getresponse()

    return verify_status(exp_status, response, "%s %s:\n%s" % (method, uri, body))





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



