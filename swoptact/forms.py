# SWOPTACT is a list of contacts with a history of their event attendance
# Copyright (C) 2015  Local Initiatives Support Corporation (LISC)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import collections

import django.forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.utils.translation import ugettext_lazy as _

from autocomplete_light import forms

from swoptact import models, widgets, formfields

class AdminLoginForm(AdminAuthenticationForm):
    """
    Provides a login form for the admin UI

    This removes the requirement for the user to have the `is_staff`
    attribute set to True. We use the admin UI for all users so this
    check and flag is redundant in this app.
    """

    error_messages = {
        "invalid_login": _("Please enter the correct %(username)s and password "
                           "for your account. Note that both fields are "
                           "case-sensitive")
    }

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise django.forms.ValidationError(
                self.error_messages["invalid_login"],
                code="invalid_login",
                params={"username": self.username_field.verbose_name}
            )

class TagAdminForm(django.forms.ModelForm):
    class Meta:
        exclude = tuple()
        model = models.Tag
        widgets = {
            "name": django.forms.TextInput(
                attrs={"size": models.Tag.get_field("name").max_length}
            ),
            "group": widgets.ForeignKeyRadioWidget(),
        }

class AutoCompleteModelForm(forms.ModelForm):
    """ Creation of new objects from text field of autocomplete fields

    When a field is using an autocomplete field and the object they're entering
    has not been created, this will create the object if the field is the only
    required field to create the object. If the object has other required fields
    this will not provide this functionality.
    """

    no_autocreate = set()

    def full_clean(self, *args, **kwargs):
        """ Look through fields to see which need models creating """
        if self.data:
            for name, field in self.fields.items():
                # If it's not an autocompletion field we're not interested.
                if not hasattr(field, "autocomplete"):
                    continue

                # We also skip anything in no_autocreate
                if name in self.no_autocreate:
                    continue

                # Turns out sometimes it has a prefix (for formsets I think)
                name = self.add_prefix(name)

                # Check if we've found a model, if we have no need to create.
                if name in self.data:
                    continue

                # Get the value entered
                value = self.data["{0}-autocomplete".format(name)]

                # If the value is empty just continue.
                if not value:
                    continue

                # Get the model and create it for value
                model = field.autocomplete.create(value)
                model.save()

                # Add the PK to the list
                self.data[name] = model.pk
        super(AutoCompleteModelForm, self).full_clean(*args, **kwargs)


# Doing this via subclassing is so dumb, but I was having trouble
# with doing it in .__init__() in AutoCompleteForm producting super weird errors
# :\
class TagSkippingAutoCompleteModelForm(AutoCompleteModelForm):
    no_autocreate = set(["tags"])


def autocomplete_modelform_factory(model, *args, **kwargs):
    """ Wrap autocomplete's modelform factory to inject our own form """
    if kwargs.get("form") is None:
        kwargs["form"] = AutoCompleteModelForm

    return forms.modelform_factory(model, *args, **kwargs)
