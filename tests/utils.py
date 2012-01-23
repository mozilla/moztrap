# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
"""
Testing utilities.

"""
import urlparse



def refresh(obj):
    """
    Return the given object as it currently exists in the database.

    """
    return obj.__class__._base_manager.get(pk=obj.pk)



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
