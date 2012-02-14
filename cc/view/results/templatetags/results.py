# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
Results-viewing template tags and filters.

"""
import math

from django import template



register = template.Library()



@register.filter
def percentage(val):
    """
    Convert a real number between 0 and 1 to a percentage from 0 to 100.

    Rounds up when under 0.5/50% and down when over. This ensures that the
    endpoints are special; we never call anything "0%" or "100%" unless it
    really is exactly that.

    """
    val = val * 100
    if val > 50:
        val = math.floor(val)
    else:
        val = math.ceil(val)
    return int(val)
