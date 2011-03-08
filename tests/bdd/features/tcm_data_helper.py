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

def compare_dicts_by_keys(exp, act, keys):
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


