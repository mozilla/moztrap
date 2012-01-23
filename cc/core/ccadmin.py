# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
CC ModelAdmin and InlineModelAdmin for use with CCModel.

"""
from itertools import chain
from functools import partial

from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet

from django.contrib import admin
from django.contrib.admin import actions
from django.contrib.admin.util import flatten_fieldsets



class CCModelAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "deleted_on"]
    readonly_fields = [
        "created_on",
        "created_by",
        "modified_on",
        "modified_by",
        "deleted_on",
        "deleted_by",
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
        queryset.delete = partial(QuerySet.delete, queryset)
        return actions.delete_selected(self, request, queryset)
    delete_selected.short_description = (
        u"PERMANENTLY delete selected %(verbose_name_plural)s")


    def save_model(self, request, obj, form, change):
        """ Given a model instance save it to the database."""
        obj.save(user=request.user)


    def save_formset(self, request, form, formset, change):
        """Given an inline formset save it to the database."""
        if isinstance(formset, CCInlineFormSet):
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
            ("created_on", "created_by"),
            ("modified_on", "modified_by"),
            ]

        delete_fields = [
            ("deleted_on", "deleted_by"),
            ]

        fieldsets = super(CCModelAdmin, self).get_fieldsets(
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


class TeamModelAdmin(CCModelAdmin):
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



class CCInlineFormSet(BaseInlineFormSet):
    def save(self, *args, **kwargs):
        """Save model instances for each form in the formset."""
        # stash the user for use by ``save_new`` and ``save_existing``
        self.user = kwargs.pop("user", None)
        return super(CCInlineFormSet, self).save(*args, **kwargs)


    def save_new(self, form, commit=True):
        """Saves and returns a new model instance for the given form."""
        form.save = partial(form.save, user=self.user)
        return super(CCInlineFormSet, self).save_new(form, commit)


    def save_existing(self, form, instance, commit=True):
        """Saves and returns an existing model instance for the given form."""
        form.save = partial(form.save, user=self.user)
        return super(CCInlineFormSet, self).save_existing(
            form, instance, commit)


    def _existing_object(self, pk):
        """Retrieve an existing inline object by pk."""
        obj = super(CCInlineFormSet, self)._existing_object(pk)
        if hasattr(self, "user"):
            obj.delete = partial(obj.delete, user=self.user)
        return obj



class CCModelForm(ModelForm):
    def save(self, commit=True, user=None):
        """Save and return this form's model instance."""
        instance = super(CCModelForm, self).save(commit=False)
        if commit:
            instance.save(user=user)
        else:
            instance.save = partial(instance.save, user=user)
        return instance



class CCInlineModelAdmin(object):
    formset = CCInlineFormSet
    form = CCModelForm
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



class CCTabularInline(CCInlineModelAdmin, admin.TabularInline):
    pass



class CCStackedInline(CCInlineModelAdmin, admin.StackedInline):
    pass
