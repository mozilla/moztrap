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
"""
Global configuration helpers for Django caching.

"""

import hashlib

from django.utils.encoding import smart_str



def make_key(key, key_prefix, version):
    """
    A cache key transformation function that hashes all keys, to avoid
    key-max-length issues.

    """
    return hashlib.sha1(
        ":".join([key_prefix, str(version), smart_str(key)])).hexdigest()
