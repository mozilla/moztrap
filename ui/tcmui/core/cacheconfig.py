"""
Global configuration helpers for Django caching.

"""

import hashlib

from django.utils.encoding import smart_str



def make_key(key, key_prefix, version):
    """
    A cache key transformation function that hashes all keys, to avoid
    key-max-length issues.

    """
    return hashlib.sha1(
        ":".join([key_prefix, str(version), smart_str(key)])).hexdigest()
