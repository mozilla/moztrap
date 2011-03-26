import floppyforms as forms



class RemoteObjectForm(forms.Form):
    pass



class AddEditForm(RemoteObjectForm):
    no_edit_fields = []
    model_choice_fields = {}
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
        for fname, kwargname in self.model_choice_fields.iteritems():
            model_choices[fname] = kwargs.pop(kwargname)

        self.auth = kwargs.pop("auth")

        initial_kwargs = kwargs.copy()

        self.instance = kwargs.pop("instance", None)
        if self.instance is not None:
            initial = kwargs.setdefault("initial", {})
            for fname in self.base_fields.iterkeys():
                initial[fname] = getattr(
                    self.instance, self.form_to_model(fname))
                if fname in self.model_choice_fields:
                    initial[fname] = initial[fname].id

        super(RemoteObjectForm, self).__init__(*args, **kwargs)

        self.model_choice_maps = {}
        for fname, model_list in model_choices.iteritems():
            choices = []
            this_map = self.model_choice_maps.setdefault(fname, {})
            for obj in model_list:
                choices.append((obj.id, obj.name))
                this_map[obj.id] = obj
            self.fields[fname].choices = choices

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
            if fname in self.model_choice_maps:
                value = self.model_choice_maps[fname][value]
            obj_dict[self.form_to_model(fname)] = value
        return obj_dict


    def handle_error(self, e):
        if e.response_error == "duplicate.name":
            self._errors["name"] = self.error_class(
                ["This name is already in use."])
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
