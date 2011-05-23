import hashlib

from django.utils.encoding import smart_str



def make_key(key, key_prefix, version):
    return hashlib.sha1(
        ":".join([key_prefix, str(version), smart_str(key)])).hexdigest()
