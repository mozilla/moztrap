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
Management forms for tags.

"""
import floppyforms as forms

from .... import model

from ...utils import ccforms




class TagForm(ccforms.NonFieldErrorsClassFormMixin, ccforms.CCModelForm):
    """Base form for tags."""
    class Meta:
        model = model.Tag
        fields = ["name", "product"]
        widgets = {
            "name": forms.TextInput,
            "product": forms.Select,
            }



class EditTagForm(TagForm):
    """Form for editing a tag."""
    def __init__(self, *args, **kwargs):
        """Initialize form; restrict tag product choices."""
        super(EditTagForm, self).__init__(*args, **kwargs)

        products_tagged = model.Product.objects.filter(
            cases__versions__tags=self.instance).distinct()
        count = products_tagged.count()

        pf = self.fields["product"]

        if count > 1:
            pf.queryset = model.Product.objects.none()
        elif count == 1:
            pf.queryset = products_tagged



class AddTagForm(TagForm):
    """Form for adding a tag."""
    pass
