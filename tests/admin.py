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
Utility base TestCase for testing admin views.

"""
from django.core.urlresolvers import reverse

from django_webtest import WebTest

from .core.builders import create_user



class AdminTestCase(WebTest):
    model_name = None
    app_label = None


    def setUp(self):
        """Set-up for all admin test cases."""
        self.user = create_user(is_staff=True, is_superuser=True)


    @property
    def changelist_url(self):
        """The changelist URL for this model."""
        return reverse(
            'admin:%s_%s_changelist' % (self.app_label, self.model_name)
            )


    @property
    def add_url(self):
        """The add URL for the given object."""
        return reverse(
            'admin:%s_%s_add' % (self.app_label, self.model_name)
            )


    def change_url(self, obj):
        """The change URL for the given object."""
        return reverse(
            'admin:%s_%s_change' % (self.app_label, self.model_name),
            args=[obj.id]
            )


    def delete_url(self, obj):
        """The delete URL for the given object."""
        return reverse(
            'admin:%s_%s_delete' % (self.app_label, self.model_name),
            args=[obj.id]
            )


    def get(self, url):
        """Make GET request to given URL and return response."""
        return self.app.get(url, user=self.user)


    def post(self, url, data):
        """Make POST request to given URL with ``data``, return response."""
        return self.app.post(url, data, user=self.user)
