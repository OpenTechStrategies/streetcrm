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
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminDateWidget
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

class ParticipantForm(django.forms.ModelForm):
    institution = formfields.BasicAutoCompleteField(
        models.Institution, "name")

    class Meta:
        model = models.Participant
        fields = "__all__"
        exclude = ("archived",)


def autocomplete_modelform_factory(model, *args, **kwargs):
    """ Wrap autocomplete's modelform factory to inject our own form """
    if kwargs.get("form") is None:
        kwargs["form"] = AutoCompleteModelForm

    return forms.modelform_factory(model, *args, **kwargs)

class SearchForm(django.forms.Form):
    """
    Form that is used to provide advanced search

    This specifically does NOT use the AutoCompleteModelForm that most forms do
    in SWOPtact because we specifically don't want the search creating new models
    if what the user wants isn't found.
    """

    PARTICIPANT = "participant"
    INSTITUTION = "institution"
    EVENT = "event"

    MODELS = (
        (PARTICIPANT, "Participants"),
        (EVENT, "Actions"),
    )

    # Regular basic search fields (must not be required as not used in advanced)
    query = django.forms.CharField(
        required=False
    )

    # Autocomplete fields
    participant = forms.ModelChoiceField(
        "ASContactAutocomplete",
        required=False
    )
    event = forms.ModelChoiceField(
        "ASEventAutocomplete",
        required=False
    )

    institution = forms.ModelChoiceField(
        "ASInstitutionAutocomplete",
        required=False
    )

    event_organizer = forms.ModelChoiceField(
        "ASContactAutocomplete",
        required=False
    )

    connected_action = forms.ModelChoiceField(
        "ASEventAutocomplete",
        required=False
    )

    event_tags = forms.ModelMultipleChoiceField(
        "ASTagAutocomplete",
        required=False
    )

    institution_tags = forms.ModelMultipleChoiceField(
        "ASTagAutocomplete",
        required=False
    )

    # None autocomplete fields
    search_model = django.forms.ChoiceField(choices=MODELS, required=False)
    exclude_major_events = django.forms.BooleanField(required=False)
    exclude_minor_events = django.forms.BooleanField(required=False)
    start_date = django.forms.DateField(
        required=False,
        widget=AdminDateWidget()
    )
    end_date = django.forms.DateField(
        required=False,
        widget=AdminDateWidget()
    )

    def clean(self, *args, **kwargs):
        # Call superclass clean method
        rtn = super(SearchForm, self).clean(*args, **kwargs)

        # Compile a list of fiedls and values to see which fields actually
        # have data in them.
        filled_fields = [(f, v) for f, v in self.cleaned_data.items() if v]

        # If none of the fields have data, the form is invalid
        if not filled_fields:
            raise ValidationError(_("You need provide query data"))

        return rtn

    def get_processed_data(self):
        """
        Provides a dictionary of submitted data collated together.

        This takes in the search data that can used when finding objects
        with autocomplete library and substitutes that as the value if no
        object has been found with autocomplete.

        In the future this might want to be moved to a mixin or a superclass
        so that it can be used with other forms.
        """
        # Form.cleaned_data only exists once Form.is_valid has been run
        self.is_valid()

        # Initially clean up the original data. The autocomplete library
        # leaves a lot of empty strings in the data so lets remove those.
        raw_data = {}

        # NB: The cast of self.data to a dictionary is required as it does not
        #     return the correct values for some reason if left as a QueryDict
        for field, value in dict(self.data).items():
            if isinstance(value, (list, tuple)):
                value = [element for element in value if element != ""]
                value = value[0] if len(value) == 1 else value
            raw_data[field] = value if value else None

        # Build up the useful data, we'll use Form.cleaned_data as a base.
        useful_data = self.cleaned_data

        for field, value in useful_data.items():
            # If it has a value, we don't need to do anything, so skip it.
            if value is not None:
                continue

            # Add the prefix, used for formsets (shouldn't apply here though)
            field = self.add_prefix(field)

            # Construct the field name for autocomplete fields
            autocomplete_field = "{field}-autocomplete".format(field=field)

            # If it doesn't exist, skip it again, nothing we can do.
            if raw_data.get(autocomplete_field, None) is None:
                continue

            # At this point there is a field and it has data, we just need to
            # copy that data to the new useful_data dictionary.
            useful_data[field] = raw_data[autocomplete_field]

        return useful_data
        
class EventForm(django.forms.ModelForm):
    organizer = formfields.BasicAutoCompleteField(
        models.Participant, "name")
    major_action = formfields.BasicAutoCompleteField(
        models.Event, "name")

    class Meta:
        model = models.Event
        fields = "__all__"
        exclude = (
            "participants", "archived")
