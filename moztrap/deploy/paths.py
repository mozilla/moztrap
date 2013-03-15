"""
Utility functions for deployment-related path-munging.

"""

import os
import sys
import site


def add_vendor_lib():
    """
    Adds the vendor library to the front of sys.path.

    """
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    vendor_lib = os.path.join(
        base_dir, "requirements", "vendor", "lib", "python")

    orig_sys_path = set(sys.path)

    # Add vendor-lib directory to sys.path (using site.addsitedir so pth
    # files are processed)
    site.addsitedir(vendor_lib)

    # Give vendor lib precedence over global Python environment
    new_sys_path = []
    for item in list(sys.path):
        if item not in orig_sys_path:
            new_sys_path.append(item)
            sys.path.remove(item)
    sys.path[:0] = new_sys_path
