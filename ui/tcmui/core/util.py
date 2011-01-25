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
