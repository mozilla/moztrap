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
Account-related forms.

"""
from django.contrib.auth import forms as auth_forms



class UpdateLabelMixin(object):
    """Mixin class to change confirmation pw field label on auth forms."""
    def __init__(self, *args, **kwargs):
        """After form initialization, change label for new_password2 field."""
        super(UpdateLabelMixin, self).__init__(*args, **kwargs)

        self.fields["new_password2"].label = "New password (again)"



class SetPasswordForm(UpdateLabelMixin, auth_forms.SetPasswordForm):
    pass



class ChangePasswordForm(UpdateLabelMixin, auth_forms.PasswordChangeForm):
    pass
