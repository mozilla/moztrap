import urllib
import urlparse

def add_to_querystring(url, **kwargs):
    """
    Add keys/values in ``kwargs`` to the querystring of ``url``.

    Based on code from remoteobjects' PromiseObject.filter method.

    """
    parts = list(urlparse.urlparse(url))
    queryargs = urlparse.parse_qs(parts[4], keep_blank_values=True)
    queryargs = dict([(k, v[0]) for k, v in queryargs.iteritems()])
    queryargs.update(kwargs)
    parts[4] = urllib.urlencode(queryargs)
    return urlparse.urlunparse(parts)



def id_for_object(val):
    """
    Return the ID for a RemoteObject. If an integer ID (or something coercible
    to one) is passed in, accept that as well.

    """
    try:
        return val.identity["@id"]
    except (AttributeError, KeyError):
        pass

    try:
        return int(val)
    except ValueError:
        pass

    raise ValueError("Values must be RemoteObject instances or integer ids, "
                     "'%r' appears to be neither." % val)
