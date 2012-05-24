"""
Models for attachments.

"""
from os.path import basename

from django.db import models

from ..mtmodel import MTModel



class Attachment(MTModel):
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
