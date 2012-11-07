"""
Utilities for dealing with URLs and querystrings.

"""
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

    # make sure all the values (such as filter params) are encoded to utf-8
    for k, v in queryargs.items():
        try:
            if isinstance(v, list):
                queryargs[k] = [x.encode("utf-8") for x in v]
        except:
            pass

    parts[4] = urllib.urlencode(queryargs, doseq=True)
    return urlparse.urlunparse(parts)
