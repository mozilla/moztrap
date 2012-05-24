"""
Testing utilities.

"""
import urlparse

from contextlib import contextmanager
from mock import patch



class Url(object):
    """
    A wrapper class for comparing urls with querystrings while avoiding
    dict-ordering dependencies. Order of keys in querystring should not matter,
    although order of multiple values for a single key does matter.

    """
    def __init__(self, url):
        self.url = url
        parts = urlparse.urlparse(url)
        self.non_qs = (
            parts.scheme,
            parts.netloc,
            parts.path,
            parts.params,
            parts.fragment)
        # convert values from lists to tuples for hashability later
        self.qs = tuple(sorted((k, tuple(v)) for k, v
                               in urlparse.parse_qs(parts.query).iteritems()))


    def __eq__(self, other):
        return (self.non_qs == other.non_qs) and (self.qs == other.qs)


    def __hash__(self):
        return hash((self.non_qs, self.qs))


    def __repr__(self):
        return "Url(%s)" % self.url



@contextmanager
def patch_session(session_data):
    """Context manager to patch session vars."""
    with patch(
            "django.contrib.sessions.backends.cached_db."
            "SessionStore._session_cache",
            session_data,
            create=True):
        yield
