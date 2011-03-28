'''
Created on Mar 8, 2011

@author: camerondawson
'''
from lettuce.terrain import world
import json
import re


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


def eq_(act, exp, msg):
    assert exp == act, "\n\tExp:%r\n\tAct:%r\n%r" % (exp, act, msg)

def eq_list_length(act_list, exp_list):
    assert len(act_list) == len(exp_list), \
        "Expect same number of values in these lists:\nExpected:\n%s\n\nActual:\n%s" % \
        (jstr(exp_list), jstr(act_list))

def compare_dicts_by_keys(exp, act, keys):
    '''
        exp = expected object
        act = actual object
        keys = tuple or list of keys that should match in both objects.  Namespace will be added to
               keys if they're not present.
    '''
    for key in keys:
        actual = act[ns(key)]
        try:
            actual = int(actual)
        except:
            pass
            # just trying to cast it to an int, if it is an int
        eq_(act[ns(key)], exp[ns(key)],
            "Field \"%s\" mismatch" % (key))

def ns_keys(dict_obj):
    '''
        Prefix the namespace to the keys in this dictionary so they'll match
        something sent back from the platform.
        Note, this only does one deep.  Second level, often needs the "@"
        prepended.  May need to support that later.
    '''
    return dict((ns(key), value) for (key, value) in dict_obj.items())

def is_subset(tcm_dict, subset_dict):
    # Verify that the result's values match our search params
    for k, v in subset_dict.items():
        if not (tcm_dict[k] == v):
            return False
    return True

# for simplicity, we just always use the same algorithm for passwords
def get_user_password(name):
    names = name.split()
    return "%s%s123" % (names[0], names[1])




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
    uri = uri.rstrip('/')
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



def list_size_check(at_least_only, exp, act):
    # if it's "exactly" these, then just make sure the lengths of the lists match,
    # otherwise, they don't need to
    if (at_least_only == "exactly"):
        passing = len(exp) == len(act)
    else:
        passing = len(exp) <= len(act)
    assert passing, \
        "These list sizes should match:\nEXPECTED:\n%s\nACTUAL:\n%s" % \
        (jstr(exp), jstr(act))

def verify_single_item_in_list(tcm_obj_list,
                               field = None,
                               exp_value = None,
                               params = None):
    if params is not None:
        ns_params = ns_keys(params)
        found_items = [x for x in tcm_obj_list if is_subset(x, ns_params)]
        assert len(found_items) == 1, \
            "Expected 1 matching item in the list for\n%s.  Found: %s\n%s" % \
            (jstr(ns_params), len(found_items), jstr(tcm_obj_list))
    else:
        found_items = [x for x in tcm_obj_list if x[ns(field)] == exp_value]
        assert len(found_items) == 1, \
            "Expected 1 matching item in the list for %s == %s.  Found: %s\n%s" % \
            (field, exp_value, len(found_items), jstr(tcm_obj_list))

    return found_items[0]

def check_first_before_second(field, first, second, obj_list):

    first_idx = [i for i, x in enumerate(obj_list) if x[ns(field)] == first]
    second_idx = [i for i, x in enumerate(obj_list) if x[ns(field)] == second]
    assert first_idx < second_idx, "Expected %s before %s in %s" % (first, second,
                                                                    jstr(obj_list))
#@todo: this should do a request.  Or perhaps we should request once before.all and build this map in memory
def get_user_status_id(user_status):
    statusMap = {"active": 1,
                 "inactive": 2,
                 "disabled": 3}
    return statusMap[user_status]

def get_result_status_id(result_status):
    statusMap = {"Pending": 1,
                 "Passed": 2,
                 "Failed": 3,
                 "Blocked": 4,
                 "Started": 5,
                 "Invalidated": 6,
                 "Skipped": 7}
    return statusMap[result_status]

def get_approval_status_id(approval_status):
    statusMap = {"Pending": 1,
                 "Approved": 2,
                 "Rejected": 3}
    return statusMap[approval_status]


def plural(tcm_type):
    '''
        Pluralize the tcm_type sent in.  This can handle namespaced or non-namespaced strings
    '''
    namespace = ""
    if tcm_type.startswith(world.ns):
        tcm_type = tcm_type[len(world.ns):]
        namespace = world.ns

    if (tcm_type == "company"):
        plural_type = "companies"
    else:
        plural_type = tcm_type + "s"

    return namespace + plural_type

def as_arrayof(tcm_type):
    return ns("ArrayOf" + tcm_type[0].capitalize() + tcm_type[1:])

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


