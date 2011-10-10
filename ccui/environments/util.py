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
from django.core.urlresolvers import reverse



def by_type(environments):
    """
    Given an iterable of ``environments``, return a dictionary mapping
    environmentType IDs to a set of environment IDs of that type in the
    iterable.

    """
    types = {}
    for env in environments:
        et = env.environmentType
        options = types.setdefault(et.id, set())
        options.add(env.id)
    return types



def environments_of(groups):
    """
    Given an iterable of environment groups, break it down into a dictionary
    mapping an (environmentType.id, environmentType.name) tuple to a set of
    (environment.id, environment.name) tuples.

    """
    types = {}
    for group in groups:
        for env in group.environments:
            et = env.environmentType
            envs = types.setdefault((et.id, et.name), set())
            envs.add((env.id, env.name))
    return types



def match(testenvs, matchenvs):
    """
    Return True if the given iterable of ``testenvs`` matches the given
    iterable of ``matchenvs``.

    If ``matchenvs`` includes multiple environments of the same type
    (e.g. Windows 7 and Windows Vista), it will match a set of environments
    containing either one of those.

    """
    types = by_type(testenvs)
    for type_id, envs in by_type(matchenvs).iteritems():
        try:
            if not types[type_id].issubset(envs):
                return False
        except KeyError:
            return False
    return True
