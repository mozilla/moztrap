# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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

from django.forms import ModelForm
from django.forms.models import BaseInlineFormSet

from django.contrib import admin



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


    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.save(user=request.user)


    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset save it to the database.
        """
        formset.save(user=request.user)


    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
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


class CCInlineFormSet(BaseInlineFormSet):
    def save(self, *args, **kwargs):
        """Save model instances for each form in the formset."""
        self.user = kwargs.pop("user", None)
        return super(CCInlineFormSet, self).save(*args, **kwargs)


    def save_new(self, form, commit=True):
        """Saves and returns a new model instance for the given form."""
        return form.save(commit=commit, user=self.user)


    def save_existing(self, form, instance, commit=True):
        """Saves and returns an existing model instance for the given form."""
        return form.save(commit=commit, user=self.user)



class CCModelForm(ModelForm):
    def save(self, commit=True, user=None):
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
