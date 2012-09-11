from tastypie.resources import ALL
from tastypie.resources import ModelResource

from .models import Tag


class TagResource(ModelResource):


    class Meta:
        queryset = Tag.objects.all()
        fields = ["name"]
        filtering = {
            "name": ALL
            }
