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
Model builders for core and external models (Product, User).

"""
user_number = 1

def create_user(**kwargs):
    global user_number

    password = kwargs.pop("password", None)
    if "username" not in kwargs:
        kwargs["username"] = "test%s" % user_number
        user_number += 1

    from django.contrib.auth.models import User

    user = User(**kwargs)
    if password:
        user.set_password(password)
    user.save()
    return user



def create_product(**kwargs):
    from cc.core.models import Product

    defaults = {
        "name": "Test Product",
        }

    defaults.update(kwargs)

    return Product.objects.create(**defaults)
