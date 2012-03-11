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
Models for attachments.

"""
from os.path import basename

from django.db import models

from ..ccmodel import CCModel



class Attachment(CCModel):
    """Abstract base class for an attachment."""
    attachment = models.FileField(upload_to="attachments/%Y/%m/%d/")
    name = models.CharField(max_length=250)


    def __unicode__(self):
        """Unicode representation is name of attached file."""
        return self.name


    class Meta:
        abstract = True


    @property
    def url(self):
        """Shortcut property to access file attachment url."""
        return self.attachment.url
