from tastypie import fields
from tastypie.resources import ModelResource

from .models import CaseVersion, Case


class CaseResource(ModelResource):

    class Meta:
        queryset = Case.objects.all()



class CaseVersionResource(ModelResource):

    case = fields.ForeignKey(CaseResource, "case")

    class Meta:
        queryset = CaseVersion.objects.all()
        fields = ["id", "name", "description", "resource_uri", "case"]



