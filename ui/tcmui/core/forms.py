from django.utils.safestring import mark_safe

import floppyforms as forms



class RemoteObjectForm(forms.Form):
    pass



class AddEditForm(RemoteObjectForm):
    no_edit_fields = []
    field_mapping = {}
    entryclass = None
    listclass = None


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

        initial_kwargs = kwargs.copy()

        self.instance = kwargs.pop("instance", None)
        if self.instance is not None:
            initial = kwargs.setdefault("initial", {})
            for fname in self.base_fields.iterkeys():
                initial[fname] = getattr(
                    self.instance, self.form_to_model(fname))

        super(RemoteObjectForm, self).__init__(*args, **kwargs)

        if self.instance is not None:
            for fname in self.no_edit_fields:
                self.fields[fname].widget = ReadOnlyWidget()

        for fname, model_list in model_choices.iteritems():
            self.fields[fname].obj_list = model_list

        self.create_formsets(*args, **initial_kwargs)


    def create_formsets(self, *args, **kwargs):
        pass


    def clean(self):
        if self.instance is None:
            return self.add_clean()
        else:
            return self.edit_clean()


    def prep_form_data(self, data, editing=False):
        """
        Takes a dictionary of form data and converts it to data ready for
        assigning to a model.

        If ``editing`` is True, ignore fields listed in ``no_edit_fields``.

        """
        obj_dict = {}
        for fname, value in self.cleaned_data.iteritems():
            if editing and fname in self.no_edit_fields:
                continue
            obj_dict[self.form_to_model(fname)] = value
        return obj_dict


    def handle_error(self, e):
        if e.response_error == "duplicate.name":
            self._errors["name"] = self.error_class(
                ["This name is already in use."])
        elif e.response_error == "changing.used.entity":
            raise forms.ValidationError(
                "This object is in use and cannot be modified."
                )
        else:
            raise forms.ValidationError(
                'Unknown conflict "%s"; please correct and try again.'
                % e.response_error)


    def add_clean(self):
        required_field_names = set(self.required_fields.iterkeys())
        if all([k in self.cleaned_data for k in required_field_names]):

            obj = self.entryclass(**self.prep_form_data(self.cleaned_data))

            try:
                self.listclass.get(auth=self.auth).post(obj)
            except self.listclass.Conflict, e:
                self.handle_error(e)
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
            self.handle_error(e)

        return self.cleaned_data



class BareTextarea(forms.Textarea):
    """
    A Textarea with no rows or cols attributes.

    """
    def __init__(self, *args, **kwargs):
        super(BareTextarea, self).__init__(*args, **kwargs)
        self.attrs = {}



class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        # If choices is set, use the display label
        displayed = dict(getattr(self, "choices", [])).get(value, value)
        return mark_safe(
            displayed + forms.HiddenInput().render(name, value, attrs))



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
                self.field.label_from_instance(obj))



class ModelChoiceField(forms.Field):
    widget = forms.Select

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
