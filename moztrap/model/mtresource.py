"""
Common api resource behavior for all MozTrap resources.

"""

from tastypie.resources import ModelResource



class MTModelResource(ModelResource):

    API_VERSION = "v1"


