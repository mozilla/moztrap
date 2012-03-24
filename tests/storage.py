"""
In-memory file storage for tests.

"""
import urlparse

from django.conf import settings
from django.utils.encoding import filepath_to_uri

import inmemorystorage



class MemoryStorage(inmemorystorage.InMemoryStorage):
    """An in-memory Django file storage backend, for tests."""
    def url(self, name):
        """In-memory files aren't actually URL-accessible; we'll pretend."""
        return urlparse.urljoin(settings.MEDIA_URL, filepath_to_uri(name))
