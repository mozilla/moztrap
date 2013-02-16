"""
Core form widgets, mixins, and fields for MozTrap.

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

from moztrap import model
from ..lists import filters



class NonFieldErrorList(ErrorList):
    """A custom ErrorList for non-field errors with "nonfield" HTML class."""
    def as_ul(self):
        if not self:
            return u''
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



class SaveIfValidMixin(object):
    """
    Form mixin class providing optimistic-locking-aware save_if_valid method.

    Can be mixed in to any form class with a ``save`` method (that accepts a
    user), a ``self.instance`` attribute, and a ``cc_version`` field.

    """
    def save_if_valid(self, user=None):
        """
        Save and return the instance if the form is valid, None if not valid.

        If the form is otherwise valid but the save fails due to another
        concurrent save getting there first, return None and add an explanatory
        error to self.errors.

        """
        if not self.is_valid():
            return None

        try:
            instance = self.save(user=user)
        except model.ConcurrencyError:
            self._errors[NON_FIELD_ERRORS] = self.error_class(
                [
                    # The link here takes advantage of the fact that an empty
                    # href links to the current page; if they reload a fresh
                    # copy of the current page (an edit form), it will show the
                    # other user's changes.
                    mark_safe(
                        u"Another user saved changes to this object in the "
                        u'meantime. Please <a href="">review their changes</a> '
                        u"and save yours again if they still apply."
                        )
                    ]
                )
            self.data = self.data.copy()
            self.data["cc_version"] = self.instance.cc_version
            return None

        return instance



class MTModelFormMetaclass(forms.models.ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        """Construct a MTModelForm subclass; ensure it has cc_version field."""
        meta = attrs.get("Meta")
        if meta:
            fields = getattr(meta, "fields", None)
            if fields is not None and "cc_version" not in fields:
                fields.append("cc_version")
        return super(MTModelFormMetaclass, cls).__new__(cls, name, bases, attrs)



class MTModelForm(SaveIfValidMixin, floppyforms.ModelForm):
    """
    A ModelForm for MTModels.

    Knows about the current user and passes it to model save. Knows about
    optimistic locking, and implements ``save_if_valid`` to allow views to
    correctly handle concurrency errors.

    """
    __metaclass__ = MTModelFormMetaclass


    def __init__(self, *args, **kwargs):
        """Initialize ModelForm. Pull out user kwarg, hide cc_version field."""
        self.user = kwargs.pop("user", None)
        super(MTModelForm, self).__init__(*args, **kwargs)
        self.fields["cc_version"].widget = floppyforms.HiddenInput()


    def save(self, commit=True, user=None):
        """
        Save and return this form's instance.

        If committing, pass user into save(). Can supply user here as well.

        This method can raise ``ConcurrencyError``; calling code not prepared
        to catch and handle ``ConcurrencyError`` should use ``save_if_valid``
        instead.

        """
        assert self.is_valid()

        instance = super(MTModelForm, self).save(commit=False)

        user = user or self.user

        if commit:
            instance.save(user=user)
            self.save_m2m()
        else:
            instance.save = partial(instance.save, user=user)

        return instance



class MTSelect(floppyforms.Select):
    """
    A Select widget for use with ``MTModelChoiceField``.

    Rendered by a template that expects each choice option's label to have an
    ``attrs`` attribute: a dictionary of arbitrary attributes to be assigned to
    the <option> element.

    """
    template_name = "forms/widgets/_select_with_option_attrs.html"



class MTSelectMultiple(floppyforms.SelectMultiple):
    """
    A SelectMultiple widget for use with ``MTModelChoiceField``.

    Rendered by a template that expects each choice option's label to have an
    ``attrs`` attribute: a dictionary of arbitrary attributes to be assigned to
    the <option> element.

    """
    template_name = "forms/widgets/_select_with_option_attrs.html"



class FilteredSelectMultiple(MTSelectMultiple):
    """
    A SelectMultiple widget that provides nice UI for filtering options.

    """
    template_name = (
        "forms/widgets/filtered_select_multiple/_filtered_select_multiple.html")
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
        try:
            ctx["choice_template"] = self.choice_template_name
        except AttributeError:
            pass
        ctx["listordering_template"] = self.listordering_template_name
        return ctx



class MTModelChoiceIterator(ModelChoiceIterator):
    """
    ModelChoiceIterator for use with ``MTModelChoiceField````.

    Returns a ``SmartLabel`` for each choice, with attrs based on the
    ``choice_attrs`` method of the field.

    """
    def choice(self, obj):
        """Return the choice tuple for the given object."""
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



def product_id_attrs(obj):
    """A ``choice_attrs`` function to label each item with its product ID."""
    return {"data-product-id": obj.product.id}



class MTModelChoiceField(forms.ModelChoiceField):
    """
    A ModelChoiceField where each choice object's label is a ``SmartLabel``.

    Accepts additional optional keyword arguments ``label_from_instance`` and
    ``choice_attrs``: each should be a one-argument callable that takes a model
    instance and returns suitable label text and a dictionary of choice
    attributes, respectively.

    """
    widget = MTSelect


    def __init__(self, *args, **kwargs):
        """Create field, checking for label_from_instance and choice_attrs."""
        self.custom_label_from_instance = kwargs.pop(
            "label_from_instance", None)

        self.custom_choice_attrs = kwargs.pop("choice_attrs", None)

        super(MTModelChoiceField, self).__init__(*args, **kwargs)


    def label_from_instance(self, obj):
        """Use custom label_from_instance method if provided."""
        if self.custom_label_from_instance is not None:
            return self.custom_label_from_instance(obj)
        return super(MTModelChoiceField, self).label_from_instance(obj)


    def _get_choices(self):
        """Use MTModelChoiceIterator."""
        if hasattr(self, "_choices"):
            return self._choices

        return MTModelChoiceIterator(self)


    choices = property(_get_choices, forms.ChoiceField._set_choices)


    def choice_attrs(self, obj):
        """Get choice attributes for a model instance."""
        if self.custom_choice_attrs is not None:
            return self.custom_choice_attrs(obj)
        return {}



class MTChoiceField(forms.ChoiceField):

    widget = MTSelect

    def valid_value(self, value):
        """
        Skip validation of values.

        The available choices are loaded on the client side, so we have
        nothing to check.

        """
        return True



class MTMultipleChoiceField(forms.MultipleChoiceField,
                                 MTChoiceField):
    widget = MTSelectMultiple



class MTModelMultipleChoiceField(forms.ModelMultipleChoiceField,
                                 MTModelChoiceField):
    widget = MTSelectMultiple



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
