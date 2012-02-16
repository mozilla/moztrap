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
Management forms for product versions.

"""
import floppyforms as forms

from .... import model

from ...utils import ccforms




class EditProductVersionForm(ccforms.NonFieldErrorsClassFormMixin,
                             ccforms.CCModelForm):
    """Form for editing productversions."""
    class Meta:
        model = model.ProductVersion
        fields = ["version", "codename"]
        widgets = {
            "version": forms.TextInput,
            "codename": forms.TextInput,
            }



class AddProductVersionForm(EditProductVersionForm):
    """Form for adding a productversion."""
    product = ccforms.CCModelChoiceField(
        queryset=model.Product.objects.all(),
        choice_attrs=lambda p: {"data-product-id": p.id})
    clone_envs_from = ccforms.CCModelChoiceField(
        required=False,
        queryset=model.ProductVersion.objects.all(),
        choice_attrs=lambda pv: {
            "data-product-id": pv.product.id,
            "data-order": pv.order
            }
        )


    class Meta(EditProductVersionForm.Meta):
        fields = ["product", "version", "codename"]
        widgets = EditProductVersionForm.Meta.widgets.copy()


    def save(self):
        """Save and return product version; copy envs."""
        pv = super(AddProductVersionForm, self).save(user=self.user)

        clone_envs_from = self.cleaned_data.get("clone_envs_from")
        if clone_envs_from:
            pv.environments.add(*clone_envs_from.environments.all())

        return pv

