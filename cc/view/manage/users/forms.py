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
Management forms for users.

"""
import floppyforms as forms

from .... import model

from ...utils import ccforms




class UserForm(ccforms.NonFieldErrorsClassFormMixin, forms.ModelForm):
    """Base form for users."""
    class Meta:
        model = model.User
        fields = ["username", "email", "is_active", "groups"]
        widgets = {
            "username": forms.TextInput,
            "email": forms.TextInput,
            "is_active": forms.CheckboxInput,
            "groups": forms.SelectMultiple,
            }


    def __init__(self, *args, **kwargs):
        """Initialize user form; labels "groups" field as "roles"."""
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields["groups"].label = "roles"



class EditUserForm(UserForm):
    """Form for editing a user."""
    pass



class AddUserForm(UserForm):
    """Form for adding a user."""
    pass
