# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
import collections
import urllib
import urlparse

import remoteobjects


# A marker value to be used for platform searches which should match
# nothing. Must be interpretable as an integer, or else searches on integer
# fields will raise 500 errors from the platform when it attempts the
# conversion.
NO_MATCH = "-999"


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
    empty (or if an empty list value is provided to begin with) use the
    NO_MATCH marker value.


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
                    new = NO_MATCH
            else:
                new = existing
        queryargs[k] = new or NO_MATCH
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
