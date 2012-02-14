# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
Core form widgets, mixins, and fields for Case Conductor.

"""
from functools import partial

from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.models import ModelChoiceIterator
from django.forms.util import ErrorList
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import force_unicode, StrAndUnicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

import floppyforms

from ..lists import filters



class NonFieldErrorList(ErrorList):
    """A custom ErrorList for non-field errors with "nonfield" HTML class."""
    def as_ul(self):
        if not self: return u''
        return mark_safe(u'<ul class="errorlist nonfield">%s</ul>'
                % ''.join([u'<li>%s</li>' % conditional_escape(force_unicode(e)) for e in self]))



class NonFieldErrorsClassFormMixin(object):
    """A Form mixin that uses NonFieldErrorList for non-field errors."""
    def _clean_form(self):
        try:
            self.cleaned_data = self.clean()
        except forms.ValidationError, e:
            self._errors[NON_FIELD_ERRORS] = NonFieldErrorList(e.messages)


    def non_field_errors(self):
        return self.errors.get(NON_FIELD_ERRORS, NonFieldErrorList())



class BareTextarea(floppyforms.Textarea):
    """A Textarea with no rows or cols attributes."""
    def __init__(self, *args, **kwargs):
        super(BareTextarea, self).__init__(*args, **kwargs)
        self.attrs = {}



class CCModelForm(floppyforms.ModelForm):
    """A ModelForm that knows about the current user and passes it to save."""
    def __init__(self, *args, **kwargs):
        """Pull user out of ModelForm initialization keyword arguments."""
        self.user = kwargs.pop("user", None)
        super(CCModelForm, self).__init__(*args, **kwargs)


    def save(self, commit=True, user=None):
        """If commiting, pass user into save(). Can supply user here as well."""
        instance = super(CCModelForm, self).save(commit=False)

        user = user or self.user

        if commit:
            instance.save(user=user)
            self.save_m2m()
        else:
            instance.save = partial(instance.save, user=user)

        return instance



class CCSelect(floppyforms.Select):
    """
    A Select widget for use with ``CCModelChoiceField``.

    Rendered by a template that expects each choice option's label to have an
    ``attrs`` attribute: a dictionary of arbitrary attributes to be assigned to
    the <option> element.

    """
    template_name = "forms/widgets/_select_with_option_attrs.html"



class CCSelectMultiple(floppyforms.SelectMultiple):
    """
    A SelectMultiple widget for use with ``CCModelChoiceField``.

    Rendered by a template that expects each choice option's label to have an
    ``attrs`` attribute: a dictionary of arbitrary attributes to be assigned to
    the <option> element.

    """
    template_name = "forms/widgets/_select_with_option_attrs.html"



class FilteredSelectMultiple(CCSelectMultiple):
    """
    A SelectMultiple widget that provides nice UI for filtering options.

    """
    template_name = (
        "forms/widgets/filtered_select_multiple/_filtered_select_multiple.html")
    choice_template_name = (
        "forms/widgets/filtered_select_multiple/"
        "_filtered_select_multiple_item.html")
    listordering_template_name = (
        "forms/widgets/filtered_select_multiple/"
        "_filtered_select_multiple_listordering.html")


    def __init__(self, *args, **kwargs):
        self.filters = kwargs.pop("filters", [])

        choice_template_name = kwargs.pop("choice_template", None)
        if choice_template_name is not None:
            self.choice_template_name = choice_template_name

        listordering_template_name = kwargs.pop("listordering_template", None)
        if listordering_template_name is not None:
            self.listordering_template_name = listordering_template_name

        super(FilteredSelectMultiple, self).__init__(*args, **kwargs)


    def get_context_data(self):
        ctx = super(FilteredSelectMultiple, self).get_context_data()
        ctx["filters"] = filters.FilterSet(self.filters).bind(MultiValueDict())
        ctx["choice_template"] = self.choice_template_name
        ctx["listordering_template"] = self.listordering_template_name
        return ctx



class CCModelChoiceIterator(ModelChoiceIterator):
    """
    ModelChoiceIterator for use with ``CCModelChoiceField````.

    Returns a ``SmartLabel`` for each choice, with attrs based on the
    ``choice_attrs`` method of the field.

    """
    def choice(self, obj):
        return (
            self.field.prepare_value(obj),
            SmartLabel(
                obj, self.field.label_from_instance, self.field.choice_attrs
                )
            )



class SmartLabel(StrAndUnicode):
    """
    A select-widget option label with smarts: also stores option attributes.

    Allows us to squeeze more data into the "label" half of the label-value
    pair of a multiple-select choice. Behaves like a simple text label if
    coerced to unicode, but also has "attrs" and "obj" attributes to access
    attributes for the choice/option, and the object itself. Useful for
    advanced multi-select widgets.

    """
    def __init__(self, obj, label_from_instance, choice_attrs):
        self.obj = obj
        self.label_from_instance = label_from_instance
        self.choice_attrs = choice_attrs


    def __unicode__(self):
        return self.label_from_instance(self.obj)


    @property
    def attrs(self):
        return self.choice_attrs(self.obj)



class CCModelChoiceField(forms.ModelChoiceField):
    """
    A ModelChoiceField where each choice object's label is a ``SmartLabel``.

    Accepts additional optional keyword arguments ``label_from_instance`` and
    ``choice_attrs``: each should be a one-argument callable that takes a model
    instance and returns suitable label text and a dictionary of choice
    attributes, respectively.

    """
    widget = CCSelect


    def __init__(self, *args, **kwargs):
        """Create field, checking for label_from_instance and choice_attrs."""
        self.custom_label_from_instance = kwargs.pop(
            "label_from_instance", None)

        self.custom_choice_attrs = kwargs.pop("choice_attrs", None)

        super(CCModelChoiceField, self).__init__(*args, **kwargs)


    def label_from_instance(self, obj):
        """Use custom label_from_instance method if provided."""
        if self.custom_label_from_instance is not None:
            return self.custom_label_from_instance(obj)
        return super(CCModelChoiceField, self).label_from_instance(obj)


    def _get_choices(self):
        """Use CCModelChoiceIterator."""
        if hasattr(self, "_choices"):
            return self._choices

        return CCModelChoiceIterator(self)


    choices = property(_get_choices, forms.ChoiceField._set_choices)


    def choice_attrs(self, obj):
        """Get choice attributes for a model instance."""
        if self.custom_choice_attrs is not None:
            return self.custom_choice_attrs(obj)
        return {}



class CCModelMultipleChoiceField(forms.ModelMultipleChoiceField,
                                 CCModelChoiceField):
    widget = CCSelectMultiple



class AutocompleteInput(floppyforms.TextInput):
    """A text input  with a data-autocomplete-url attribute and ul.suggest."""
    template_name = "forms/widgets/_autocomplete_input.html"


    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop("url")
        super(AutocompleteInput, self).__init__(*args, **kwargs)


    def render(self, name, value, attrs=None, extra_context={}):
        attrs = attrs or {}
        attrs["data-autocomplete-url"] = (
            self.url() if callable(self.url) else self.url)
        attrs["autocomplete"] = "off"
        return super(AutocompleteInput, self).render(
            name, value, attrs, extra_context)
