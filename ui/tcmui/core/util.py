import collections
import urllib
import urlparse



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
            if (isinstance(v, basestring) or
                not isinstance(v, collections.Iterable)):
                queryargs[k].append(v)
            else:
                queryargs[k].extend(v)
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



def lc_first(s):
    return s[0].lower() + s[1:]
