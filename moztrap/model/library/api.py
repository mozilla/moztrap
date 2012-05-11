from tastypie.resources import ALL
from tastypie import fields
from tastypie.resources import ModelResource

from .models import CaseVersion, Case
from ..environments.api import EnvironmentResource


class CaseResource(ModelResource):

    class Meta:
        queryset = Case.objects.all()



class CaseVersionResource(ModelResource):

    case = fields.ForeignKey(CaseResource, "case")
    environments = fields.ToManyField(EnvironmentResource, "environments")

    class Meta:
        queryset = CaseVersion.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "name", "description", "resource_uri", "case"]
        filtering = {"environments": ALL}



