"""
MT ModelAdmin and InlineModelAdmin for use with MTModel.

"""
from itertools import chain
from functools import partial

from django.conf import settings
from django.forms.models import BaseInlineFormSet
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from django.contrib import admin, messages
from django.contrib.admin import actions
from django.contrib.admin.util import flatten_fieldsets
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login

from moztrap.view.utils.mtforms import MTModelForm



class MTAdminSite(admin.AdminSite):
    """MozTrap admin site class."""
    @never_cache
    def login(self, request, extra_context=None):
        """Displays the login form for the given HttpRequest."""
        if request.user.is_authenticated():
            messages.warning(
                request,
                "Your account does not have permissions to access that page. "
                "Please log in with a different account, or visit a different "
                "page. "
                )
        return redirect_to_login(
            request.get_full_path(),
            settings.LOGIN_URL,
            REDIRECT_FIELD_NAME,
            )


    @never_cache
    def logout(self, request, extra_context=None):
        """
        Make admin 'logout' a no-op.

        We replace the link with a "back to MozTrap" link.

        The default AdminSite.logout implementation exposes us to logout CSRF.

        """
        return redirect("home")


site = MTAdminSite()



class MTModelAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "deleted_on"]
    readonly_fields = [
        "created_on",
        "created_by",
        "modified_on",
        "modified_by",
        "deleted_on",
        "deleted_by",
        "cc_version",
        ]
    actions = ["delete", "undelete", "delete_selected"]


    def delete(self, request, queryset):
        """Admin action to soft-delete objects."""
        queryset.delete(user=request.user)
    delete.short_description = (
        u"Delete selected %(verbose_name_plural)s")


    def undelete(self, request, queryset):
        """Admin action to undelete objects."""
        queryset.undelete(user=request.user)
    undelete.short_description = (
        u"Undelete selected %(verbose_name_plural)s")


    def delete_selected(self, request, queryset):
        """Bypass soft delete and really delete selected instances."""
        queryset.delete = partial(queryset.delete, permanent=True)
        return actions.delete_selected(self, request, queryset)
    delete_selected.short_description = (
        u"PERMANENTLY delete selected %(verbose_name_plural)s")


    def save_model(self, request, obj, form, change):
        """Given a model instance save it to the database."""
        obj.save(user=request.user)


    def save_formset(self, request, form, formset, change):
        """Given an inline formset save it to the database."""
        if isinstance(formset, MTInlineFormSet):
            formset.save(user=request.user)
        else:
            formset.save()


    def delete_model(self, request, obj):
        """Given a model instance delete it from the database."""
        obj.delete(user=request.user)


    def get_fieldsets(self, *args, **kwargs):
        """
        Get fieldsets for the add/change form.

        Adds separate fieldsets at the end for metadata fields
        (creation/modification/deletion tracking), and removes these from
        default all-fields fieldset, if present.

        """
        meta_fields = [
            ("cc_version",),
            ("created_on", "created_by"),
            ("modified_on", "modified_by"),
            ]

        delete_fields = [
            ("deleted_on", "deleted_by"),
            ]

        fieldsets = super(MTModelAdmin, self).get_fieldsets(
            *args, **kwargs)[:]

        if not self.declared_fieldsets:
            metadata_fields = set(
                chain.from_iterable(chain(meta_fields, delete_fields)))

            fieldsets[0][1]["fields"] = [
                field for field in fieldsets[0][1]["fields"]
                if field not in metadata_fields
                ]

        fieldsets.extend([
                ("Deletion", {"fields": delete_fields}),
                ("Meta", {"fields": meta_fields, "classes": ["collapse"]})
                ])

        return fieldsets


class TeamModelAdmin(MTModelAdmin):
    def get_fieldsets(self, *args, **kwargs):
        """
        Get fieldsets for the add/change form.

        Adds separate fieldset at the end for Team fields, and removes these
        from default all-fields fieldset, if present.

        """
        team_fields = [("has_team", "own_team")]

        fieldsets = super(TeamModelAdmin, self).get_fieldsets(
            *args, **kwargs)[:]

        if not self.declared_fieldsets:
            metadata_fields = set(chain.from_iterable(team_fields))

            fieldsets[0][1]["fields"] = [
                field for field in fieldsets[0][1]["fields"]
                if field not in metadata_fields
                ]

        # Place Team fieldset right before Deletion and Meta
        fieldsets.insert(-2, ("Team", {"fields": team_fields}))

        return fieldsets


    def get_form(self, *args, **kwargs):
        """
        Get form for use in admin add/change view.

        Ensures that team fields are included in form, even when fieldsets are
        explicitly specified and don't include the team fieldset (because it is
        automatically added by ``get_fieldsets``).

        """
        if self.declared_fieldsets:
            kwargs["fields"] = flatten_fieldsets(
                self.declared_fieldsets) + ["has_team", "own_team"]

        return super(TeamModelAdmin, self).get_form(*args, **kwargs)



class MTInlineFormSet(BaseInlineFormSet):
    def save(self, *args, **kwargs):
        """Save model instances for each form in the formset."""
        # stash the user for use by ``save_new`` and ``save_existing``
        self.user = kwargs.pop("user", None)
        return super(MTInlineFormSet, self).save(*args, **kwargs)


    def save_new(self, form, commit=True):
        """Saves and returns a new model instance for the given form."""
        form.save = partial(form.save, user=self.user)
        return super(MTInlineFormSet, self).save_new(form, commit)


    def save_existing(self, form, instance, commit=True):
        """Saves and returns an existing model instance for the given form."""
        form.save = partial(form.save, user=self.user)
        return super(MTInlineFormSet, self).save_existing(
            form, instance, commit)


    def _existing_object(self, pk):
        """Retrieve an existing inline object by pk."""
        obj = super(MTInlineFormSet, self)._existing_object(pk)
        if hasattr(self, "user"):
            obj.delete = partial(obj.delete, user=self.user)
        return obj



class MTInlineModelAdmin(object):
    formset = MTInlineFormSet
    form = MTModelForm
    # metadata fields are too much cruft for an inline
    exclude = [
        "created_on",
        "created_by",
        "modified_on",
        "modified_by",
        "deleted_on",
        "deleted_by",
        ]

    readonly_fields = ["exists"]


    def exists(self, obj):
        return obj.deleted_on is None
    exists.boolean = True



class MTTabularInline(MTInlineModelAdmin, admin.TabularInline):
    pass



class MTStackedInline(MTInlineModelAdmin, admin.StackedInline):
    pass
