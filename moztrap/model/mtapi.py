from django.db.models import Q
from django.db.models.sql.constants import QUERY_TERMS, LOOKUP_SEP
from django.utils.datastructures import MultiValueDict

from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import  Authorization
from .core.models import ApiKey

import logging, sys, traceback

logger = logging.getLogger("moztrap.model.mtapi")

class MTApiKeyAuthentication(ApiKeyAuthentication):
    """Authentication that requires our custom api key implementation."""

    def get_key(self, user, api_key):
        try:
            ApiKey.objects.get(owner=user, key=api_key, active=True)
            logger.debug("api key is authorized")
        except Exception as e:
            logger.debug("api key is NOT authorized\n%s" % e)
            return self._unauthorized()

        return True


    def is_authenticated(self, request, **kwargs):
        """
        Finds the user and checks their API key. GET requests are always
        allowed.

        This overrides Tastypie's default impl, because we use a User
        proxy class, which Tastypie doesn't find

        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """
        if request.method == "GET":
            return True

        from .core.auth import User

        username = request.GET.get("username") or request.POST.get("username")
        api_key = request.GET.get("api_key") or request.POST.get("api_key")

        if not username or not api_key:
            if not username:  # pragma: no cover
                logger.debug("no username")  # pragma: no cover
            elif not api_key:  # pragma: no cover
                logger.debug("no api key")  # pragma: no cover
            return self._unauthorized()

        try:
            user = User.objects.get(username=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            logger.debug("user retrieval error")
            return self._unauthorized()

        request.user = user
        return self.get_key(user, api_key)



class MTAuthorization(Authorization):
    """Authorization that allows any user to GET but only users with permissions
    to modify."""

    @property
    def permission(self):
        """This permission should be checked by is_authorized."""
        klass = self.resource_meta.object_class
        permission = "%s.manage_%ss" % (klass._meta.app_label,
            klass._meta.module_name)
        logger.debug("desired permission %s" % permission)
        return permission

    def is_authorized(self, request, object=None):

        if request.method == "GET":
            logger.debug("GET always allowed")
            return True
        elif request.user.has_perm(self.permission):
            logger.debug("user has permissions")
            return True
        else:
            logger.debug("user does not have permissions")
            return False



class MTResource(ModelResource):
    """Implement the common code needed for CRUD API interfaces.

    Child classes must implement the following abstract methods:

    - model (property)

    """

    class Meta:
        list_allowed_methods = ["get", "post"]
        detail_allowed_methods = ["get", "put", "delete"]
        authentication = MTApiKeyAuthentication()
        authorization = MTAuthorization()
        always_return_data = True
        ordering = ['id']

    @property
    def model(self):
        """Model class related to this resource."""
        raise NotImplementedError  # pragma: no cover


    def obj_create(self, bundle, request=None, **kwargs):
        """Set the created_by field for the object to the request's user"""
        # this try/except logging is more helpful than 500 / 404 errors on
        # the client side
        try:
            bundle = super(MTResource, self).obj_create(
                bundle=bundle, request=request, **kwargs)
            bundle.obj.created_by = request.user
            bundle.obj.save(user=request.user)
            return bundle
        except Exception as e:  # pragma: no cover
            logger.exception("error creating")  # pragma: no cover
            raise e  # pragma: no cover


    def obj_update(self, bundle, request=None, **kwargs):
        """Set the modified_by field for the object to the request's user"""
        # this try/except logging is more helpful than 500 / 404 errors on the
        # client side
        try:
            bundle = super(MTResource, self).obj_update(
                bundle=bundle, request=request, **kwargs)
            bundle.obj.save(user=request.user)
            return bundle
        except Exception as e:  # pragma: no cover
            logger.exception("error updating")  # pragma: no cover
            raise e # pragma: no cover


    def obj_delete(self, request=None, **kwargs):
        """Delete the object.
        The DELETE request may include permanent=True/False in its params
        parameter (ie, along with the user's credentials). Default is False.
        """
        # this try/except logging is more helpful than 500 / 404 errors on
        # the client side
        try:
            permanent = request._request.dicts[1].get("permanent", False)
            # pull the id out of the request's path
            obj_id = request.path.split('/')[-2]
            obj = self.model.objects.get(id=obj_id)
            obj.delete(user=request.user, permanent=permanent)
        except Exception:  # pragma: no cover
            logger.exception("error deleting")  # pragma: no cover
            raise  # pragma: no cover


    def delete_detail(self, request, **kwargs):
        """Avoid the following error:
        WSGIWarning: Content-Type header found in a 204 response, which not
        return content.
        """
        res = super(MTResource, self).delete_detail(request, **kwargs)
        del(res._headers["content-type"])
        return res



class MTBaseSelectionResource(ModelResource):
    """Adds filtering by negation for use with multi-select widget"""

    def apply_filters(self,
                      request,
                      applicable_includes,
                      applicable_excludes={},
                      ):
        """Apply included and excluded filters to query."""
        applicable_filters = self.convert_to_Q(applicable_includes)
        return self.get_object_list(request).filter(
            applicable_filters).exclude(**applicable_excludes.dict())


    def convert_to_Q(self, applicable_includes):
        """Make this multivalue dict use OR for items that are multiple."""
        filters = Q()
        for key, list_values in applicable_includes.lists():
            if len(list_values) == 1:
                new_q = Q(**{key: list_values[0]})
            else:
                for item in list_values:
                    new_q = new_q | Q(**{key: item})

            filters &= (new_q)

        return filters


    def obj_get_list(self, request=None, **kwargs):
        """Return the list with included and excluded filters, if they exist."""
        filters = MultiValueDict()

        # if there is more than one value for a field (like tags)
        # then we want the key to have __in so it can be any of
        # those values.  Otherwise, it would just be the last one
        # in the list, ignoring other values.
        if hasattr(request, 'GET'): # pragma: no cover
            # Grab a mutable copy.
#            for key in request.GET:
#                qlist = request.GET.getlist(key)
#                if len(qlist) > 1:
#                    qkey = "{0}__in".format(key)
#                else:
#                    qkey = key
#                filters[qkey] = ",".join(request.GET.getlist(key))
            filters = request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)

        # Splitting out filtering and excluding items
        new_filters = MultiValueDict()
        excludes = MultiValueDict()
        for key, value_list in filters.lists():
            # If the given key is filtered by ``not equal`` token, exclude it
            if key.endswith('__ne'):
                key = key[:-4] # Stripping out trailing ``__ne``
                excludes.setlist(key, value_list)
            else:
                new_filters.setlist(key, value_list)

        filters = new_filters

        # Building filters
        applicable_includes = self.build_filters(filters=new_filters)
        applicable_excludes = self.build_filters(filters=excludes)

        base_object_list = self.apply_filters(
            request, applicable_includes, applicable_excludes)
        return self.apply_authorization_limits(request, base_object_list)


    def build_filters(self, filters=None):
        """
        Given a dictionary of filters, create the necessary ORM-level filters.

        Supports multiple filtering on the same field with a multi-value-dict.
        """
        if filters is None:
            filters = MultiValueDict()

        qs_filters = MultiValueDict()

        if hasattr(self._meta, 'queryset'):
            # Get the possible query terms from the current QuerySet.
            query_terms = self._meta.queryset.query.query_terms.keys()
        else:
            query_terms = QUERY_TERMS.keys()

        for filter_expr, values_list in filters.lists():
            filter_bits = filter_expr.split(LOOKUP_SEP)
            field_name = filter_bits.pop(0)
            filter_type = 'exact'

            if not field_name in self.fields:
                # It's not a field we know about. Move along citizen.
                continue

            if len(filter_bits) and filter_bits[-1] in query_terms:
                filter_type = filter_bits.pop()

            from tastypie.resources import ModelResource
            lookup_bits = self.check_filtering(field_name, filter_type, filter_bits)
            new_values_list = [self.filter_value_to_python(
                x, field_name, filters, filter_expr, filter_type
                ) for x in values_list]

            db_field_name = LOOKUP_SEP.join(lookup_bits)
            qs_filter = "%s%s%s" % (db_field_name, LOOKUP_SEP, filter_type)
            qs_filters.setlist(str(qs_filter), new_values_list)

        return qs_filters


    def filter_value_to_python(self, value, field_name, filters, filter_expr,
                               filter_type):
        """
        Turn the string ``value`` into a python object.
        """
        # Simple values
        if value in ['true', 'True', True]:
            value = True
        elif value in ['false', 'False', False]:
            value = False
        elif value in ('nil', 'none', 'None', None):
            value = None

        # Split on ',' if not empty string and either an in or range filter.
        if filter_type in ('in', 'range') and len(value):
            if hasattr(filters, 'getlist'):
                value = []

                for part in filters.getlist(filter_expr):
                    value.extend(part.split(','))
            else:
                value = value.split(',')

        return value
