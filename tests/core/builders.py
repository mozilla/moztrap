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
from ..builder import ListBuilder


companies = ListBuilder(
    "company",
    "companies",
    "Company",
    {
        "name": "Default company name",
        "address": "Default company address",
        "city": "Default company city",
        "country": 239,
        "phone": "123-456-7890",
        "url": "www.example.com",
        "zip": "12345",
        })



cvis = ListBuilder(
    "CategoryValueInfo",
    None,
    "CategoryValueInfo",
    {
        "categoryName": 1,
        "categoryValue": 1,
        },
    add_identity=False,
    add_timeline=False)
