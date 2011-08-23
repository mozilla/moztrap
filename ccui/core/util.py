import collections
import urllib
import urlparse

import remoteobjects



def update_querystring(url, **kwargs):
    """
    Updates the querystring of ``url`` with keys/values in ``kwargs``,
    replacing any existing values for those querystring keys, and removing any
    keys set to None in ``kwargs``. Any values that are lists will be converted
    to multiple querystring keys.

    """
    parts = list(urlparse.urlparse(url))
    queryargs = urlparse.parse_qs(parts[4], keep_blank_values=False)
    for k, v in kwargs.iteritems():
        if v is None:
            del queryargs[k]
        else:
            queryargs[k] = v
    parts[4] = urllib.urlencode(queryargs, doseq=True)
    return urlparse.urlunparse(parts)



def narrow_querystring(url, **kwargs):
    """
    Updates the querystring of ``url`` with keys/values in ``kwargs``,
    performing only updates that would further narrow the set of returned
    objects if this querystring is used as a filter. In other words, only apply
    the intersection of values for any given key, and if that intersection is
    empty use the marker value ``__`` which should match nothing.


    """
    parts = list(urlparse.urlparse(url))
    queryargs = urlparse.parse_qs(parts[4], keep_blank_values=False)
    for k, v in kwargs.iteritems():
        new = convert_to_list(v)
        if k in queryargs:
            existing = convert_to_list(queryargs[k])
            if new:
                # no use of sets here, order matters
                new = [o for o in new if o in existing]
                if not new:
                    new = str("__")
            else:
                new = existing
        queryargs[k] = new
    parts[4] = urllib.urlencode(queryargs, doseq=True)
    return urlparse.urlunparse(parts)



def add_to_querystring(url, **kwargs):
    """
    Add keys/values in ``kwargs`` to querystring of ``url``, without removing
    any existing values. Any values that are lists will be converted to
    multiple querystring keys.

    """
    parts = list(urlparse.urlparse(url))
    queryargs = urlparse.parse_qs(parts[4], keep_blank_values=False)
    for k, v in kwargs.iteritems():
        if k in queryargs:
            queryargs[k].extend(convert_to_list(v))
        else:
            queryargs[k] = v
    parts[4] = urllib.urlencode(queryargs, doseq=True)
    return urlparse.urlunparse(parts)



def id_for_object(val):
    """
    Return the ID for a RemoteObject. If an integer ID (or something coercible
    to one) is passed in, accept that as well.

    """
    try:
        if val.identity is None:
            return None
        return val.identity["@id"]
    except (AttributeError, KeyError):
        pass

    try:
        return int(val)
    except (ValueError, TypeError):
        pass

    raise ValueError("Values must be RemoteObject instances or integer ids, "
                     "'%r' appears to be neither." % val)



def prep_for_query(val, encode_callback=None, accept_iterables=True):
    """
    Convert a value (or list of values, if ``accept_iterables`` is True) to a
    value (or list of values) suitable for submission to the API in a
    querystring. ``accept_iterables`` is not recursive; nested iterables are
    never valid.

    ``encode_callback`` can be a callable that takes a single argument, each
    value will be passed through this callable if it is given.

    Does not do url-encoding; returned value is string or list of strings
    suitable as argument to ``narrow_querystring`` or ``update_querystring`` or
    ``add_to_querystring``, which will use urllib.urlencode.

    """
    # RemoteObject instances are iterable but a single filter value
    if (accept_iterables and is_iterable(val) and
        not isinstance(val, remoteobjects.RemoteObject)):
        return [prep_for_query(elem, encode_callback, False) for elem in val]

    if encode_callback is not None:
        val = encode_callback(val)

    return str(val)



def lc_first(s):
    return s[0].lower() + s[1:]



def is_iterable(v):
    return ((not isinstance(v, basestring) and
             isinstance(v, collections.Iterable)))



def convert_to_list(v):
    if not is_iterable(v):
        return [v]
    return list(v)



def get_action(post_data):
    """
    Given a request.POST including e.g. {"action-delete": "3"}, return
    ("delete", "3"). Doesn't care about the value, just looks for POST keys
    beginning with "action-". Returns None if no action found.

    If multiple actions are found, returns only the first.

    """
    actions = [
        (k[len("action-"):], v) for k, v in post_data.iteritems()
        if k.startswith("action-")
        ]
    if actions:
        return actions[0]
    return None
