from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

import floppyforms as forms

from . import errors



class NonFieldErrorList(ErrorList):
    def as_ul(self):
        if not self: return u''
        return mark_safe(u'<ul class="errorlist nonfield">%s</ul>'
                % ''.join([u'<li>%s</li>' % conditional_escape(force_unicode(e)) for e in self]))



class NonFieldErrorsClassFormMixin(object):
    def _clean_form(self):
        try:
            self.cleaned_data = self.clean()
        except forms.ValidationError, e:
            self._errors[NON_FIELD_ERRORS] = NonFieldErrorList(e.messages)


    def non_field_errors(self):
        return self.errors.get(NON_FIELD_ERRORS, NonFieldErrorList())



class RemoteObjectForm(NonFieldErrorsClassFormMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super(RemoteObjectForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field, forms.DateField):
                field.widget.attrs.setdefault("placeholder", "mm/dd/yyyy")



class AddEditForm(RemoteObjectForm):
    no_edit_fields = []
    field_mapping = {}
    assign_later = []
    entryclass = None
    listclass = None
    extra_creation_data = {}


    def form_to_model(self, formfield):
        return self.field_mapping.get(formfield, formfield)


    def model_to_form(self, modelfield):
        return self.reverse_mapping.get(modelfield, modelfield)


    @property
    def reverse_mapping(self):
        return dict((v, k) for (k, v) in self.field_mapping.iteritems())


    @property
    def required_fields(self):
        return dict((n, f) for (n, f) in self.fields.iteritems()
                    if f.required)


    @property
    def optional_fields(self):
        return dict((n, f) for (n, f) in self.fields.iteritems()
                    if not f.required)


    def __init__(self, *args, **kwargs):
        model_choices = {}
        for fname, field in self.base_fields.iteritems():
            if hasattr(field, "obj_list"):
                model_choices[fname] = kwargs.pop("%s_choices" % fname)

        self.auth = kwargs.pop("auth")

        formset_kwargs = kwargs.copy()
        formset_kwargs.pop("initial", None)

        self.instance = kwargs.pop("instance", None)
        if self.instance is not None:
            initial = kwargs.setdefault("initial", {})
            for fname in self.base_fields.iterkeys():
                initial[fname] = getattr(
                    self.instance, self.form_to_model(fname))

        super(AddEditForm, self).__init__(*args, **kwargs)

        if self.instance is not None:
            for fname in self.no_edit_fields:
                self.fields[fname].widget = ReadOnlyWidget()

        for fname, model_list in model_choices.iteritems():
            self.fields[fname].obj_list = model_list

        self.create_formsets(*args, **formset_kwargs)


    def create_formsets(self, *args, **kwargs):
        pass


    def clean(self):
        if self.instance is None:
            cleaned = self.add_clean()
            editing = False
        else:
            cleaned = self.edit_clean()
            editing = True
        if self.instance is not None:
            try:
                for fname, value in self.prep_assign_later_data(
                    cleaned).iteritems():
                    setattr(self.instance, fname, value)
                    self.instance = self.instance.refresh()
            except self.instance.Conflict, e:
                if not editing:
                    self.instance.delete()
                self.handle_error(self.instance, e)
        return cleaned


    def prep_form_data(self, data, editing=False, immediate=True):
        """
        Takes a dictionary of form data and converts it to data ready for
        assigning to a model.

        If ``editing`` is True, ignore fields listed in ``no_edit_fields``.

        """
        obj_dict = {}
        for fname, value in data.iteritems():
            if immediate and fname in self.assign_later:
                continue
            if editing and fname in self.no_edit_fields:
                continue
            obj_dict[self.form_to_model(fname)] = value
        return obj_dict


    def prep_assign_later_data(self, data, editing=False):
        return self.prep_form_data(
            dict((k, v) for k, v in data.iteritems() if k in self.assign_later),
            editing=editing,
            immediate=False)


    def handle_error(self, obj, err):
        message, fields = errors.error_message_and_fields(obj, err)
        for fname in fields:
            if fname in self.fields:
                self._errors[fname] = self.error_class(
                    [message])
                return
        raise forms.ValidationError(message)


    def add_clean(self):
        required_field_names = set(self.required_fields.iterkeys())
        if all([k in self.cleaned_data for k in required_field_names]):

            obj = self.entryclass(
                **dict(
                    self.prep_form_data(self.cleaned_data),
                    **self.extra_creation_data))

            try:
                self.listclass.get(auth=self.auth).post(obj)
            except self.listclass.Conflict, e:
                self.handle_error(obj, e)
            else:
                self.instance = obj

        return self.cleaned_data


    def edit_clean(self):
        for k, v in self.prep_form_data(
            self.cleaned_data, editing=True).iteritems():
            setattr(self.instance, k, v)
        try:
            self.instance.put()
        except self.instance.Conflict, e:
            self.handle_error(self.instance, e)

        return self.cleaned_data


    def save(self):
        return self.instance



class BareTextarea(forms.Textarea):
    """
    A Textarea with no rows or cols attributes.

    """
    def __init__(self, *args, **kwargs):
        super(BareTextarea, self).__init__(*args, **kwargs)
        self.attrs = {}



class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        # work around floppyforms bug with no attrs:
        if attrs is None:
            attrs = {}
        # If choices is set, use the display label
        displayed = str(dict((o[:2] for o in getattr(self, "choices", []))).get(
            value, value))
        return mark_safe(
            displayed + forms.HiddenInput().render(name, value, attrs))



class OptionAttrsSelect(forms.Select):
    """
    A SelectMultiple widget rendered by a template that expects each choice
    option to have a third tuple element (in addition to value and label): a
    dictionary of arbitrary attributes to be assigned to the <option> element.

    """
    template_name = "forms/_select_with_option_attrs.html"



class OptionAttrsSelectMultiple(forms.SelectMultiple):
    """
    A SelectMultiple widget rendered by a template that expects each choice
    option to have a third tuple element (in addition to value and label): a
    dictionary of arbitrary attributes to be assigned to the <option> element.

    """
    template_name = "forms/_select_with_option_attrs.html"



class ModelChoiceIterator(object):
    def __init__(self, field):
        self.field = field
        self.obj_list = field.obj_list

    def __iter__(self):
        if self.field.empty_label is not None:
            yield (u"", self.field.empty_label)
        if self.field.cache_choices:
            if self.field.choice_cache is None:
                self.field.choice_cache = [
                    self.choice(obj) for obj in self.obj_list
                ]
            for choice in self.field.choice_cache:
                yield choice
        else:
            for obj in self.obj_list:
                yield self.choice(obj)

    def __len__(self):
        return len(self.obj_list)

    def choice(self, obj):
        return (self.field.prepare_value(obj),
                self.field.label_from_instance(obj),
                self.field.option_attrs(obj))



class ModelChoiceField(forms.Field):
    widget = OptionAttrsSelect

    default_error_messages = {
        "invalid_choice": u"Select a valid choice. That choice is not one of"
                          u" the available choices.",
    }


    def __init__(self, empty_label=u"---------", cache_choices=False,
                 required=True, widget=None, label=None, initial=None,
                 help_text=None, *args, **kwargs):
        if required and (initial is not None):
            self.empty_label = None
        else:
            self.empty_label = empty_label
        self.cache_choices = cache_choices

        self.custom_label_from_instance = kwargs.pop(
            "label_from_instance", None)

        self.custom_option_attrs = kwargs.pop("option_attrs", None)

        super(ModelChoiceField, self).__init__(
            required, widget, label, initial, help_text, *args, **kwargs)

        self.obj_list = []
        self.choice_cache = None


    def _get_obj_list(self):
        return self._obj_list


    def _set_obj_list(self, obj_list):
        self._obj_list = obj_list
        self._obj_map = {}
        for obj in obj_list:
            self._obj_map[obj.id] = obj
        self.widget.choices = self.choices


    obj_list = property(_get_obj_list, _set_obj_list)


    def label_from_instance(self, obj):
        if self.custom_label_from_instance is not None:
            return self.custom_label_from_instance(obj)
        return unicode(obj)


    def _get_choices(self):
        # If self._choices is set, then somebody must have manually set
        # the property self.choices. In this case, just return self._choices.
        if hasattr(self, "_choices"):
            return self._choices

        # Otherwise, iterate over self.obj_list to determine the choices
        # dynamically. Return a fresh ModelChoiceIterator that has not been
        # consumed. This construct might look complicated but it allows for
        # lazy evaluation of the object list.
        return ModelChoiceIterator(self)


    choices = property(_get_choices, forms.ChoiceField._set_choices)


    def prepare_value(self, value):
        try:
            return value.id
        except AttributeError:
            return super(ModelChoiceField, self).prepare_value(value)


    def option_attrs(self, obj):
        if self.custom_option_attrs is not None:
            return self.custom_option_attrs(obj)
        return {}


    def to_python(self, value):
        if value in [None, "", [], (), {}]:
            return None
        try:
            value = self._obj_map[value]
        except KeyError:
            raise forms.ValidationError(self.error_messages['invalid_choice'])
        return value


    def validate(self, value):
        return forms.Field.validate(self, value)


class ModelMultipleChoiceField(ModelChoiceField):
    widget = OptionAttrsSelectMultiple
    hidden_widget = forms.MultipleHiddenInput
    default_error_messages = {
        "list": u"Enter a list of values.",
        "invalid_choice": u"Select a valid choice. %s is not one of the"
                            u" available choices.",
    }

    def __init__(self, cache_choices=False, required=True,
                 widget=None, label=None, initial=None,
                 help_text=None, *args, **kwargs):
        super(ModelMultipleChoiceField, self).__init__(None,
            cache_choices, required, widget, label, initial, help_text,
            *args, **kwargs)

    def clean(self, value):
        if self.required and not value:
            raise forms.ValidationError(self.error_messages["required"])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise forms.ValidationError(self.error_messages["list"])

        objs = []
        for val in value:
            try:
                objs.append(self._obj_map[val])
            except KeyError:
                raise forms.ValidationError(
                    self.error_messages["invalid_choice"] % val)
        # Since this overrides the inherited ModelChoiceField.clean
        # we run custom validators here
        self.run_validators(value)
        return objs

    def prepare_value(self, value):
        if hasattr(value, "entries"):
            return [super(ModelMultipleChoiceField, self).prepare_value(v) for v
                    in value]
        return super(ModelMultipleChoiceField, self).prepare_value(value)
