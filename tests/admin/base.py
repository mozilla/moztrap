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

from ..builders import create_user



class AdminTestCase(WebTest):
    model_name = None
    app_label = None


    def setUp(self):
        self.user = create_user(is_staff=True, is_superuser=True)


    @property
    def changelist_url(self):
        return reverse(
            'admin:%s_%s_changelist' % (self.app_label, self.model_name)
            )


    def change_url(self, obj):
        return reverse(
            'admin:%s_%s_change' % (self.app_label, self.model_name),
            args=[obj.id]
            )


    def get(self, url):
        return self.app.get(url, user=self.user)
