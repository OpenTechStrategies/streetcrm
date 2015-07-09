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

import datetime
import phonenumbers

from django import forms
from django.core import validators, exceptions
from django.utils.translation import ugettext_lazy as _, ungettext_lazy

from phonenumber_field import formfields

from swoptact import widgets

class LocalPhoneNumberField(formfields.PhoneNumberField):
    """ National representation of phone number """

    widget = widgets.LocalPhoneNumberWidget

    def to_python(self, value, *args, **kwargs):
        """ Convert value from National US phone number to international """
        if value in validators.EMPTY_VALUES:
            value = None
        else:
            # Parse the value
            try:
                if value.startswith("+"):
                    value = phonenumbers.parse(value)
                else:
                    value = phonenumbers.parse(value, "US")
            except phonenumbers.phonenumberutil.NumberParseException:
                value = phonenumbers.PhoneNumber(raw_input=value)

            # Produce international format without formatting.
            value = "+{country_code}{national_number}".format(
                country_code=value.country_code,
                national_number=value.national_number
            )

        return super(LocalPhoneNumberField, self).to_python(
            value, *args, **kwargs
        )

class TwelveHourTimeField(forms.TimeField):
    widget = widgets.TwelveHourTimeWidget
    default_error_messages = {
        "invalid": _("Enter a valid time."),
        "invalid_suffix": _("Select am or pm."),
    }

    def to_python(self, value):
        """ Convert time to datetime.time object """
        time, suffix = value

        # If no time has been specified we'll get ["", ""]
        if time in self.empty_values and suffix in self.empty_values:
            return None

        # If no suffix has been supplied then we should display an error
        if time not in self.empty_values and suffix in self.empty_values:
            raise exceptions.ValidationError(
                self.error_messages["invalid_suffix"],
                code="invalid"
            )

        # If the time suffix has been supplied without a time we should check
        # that too
        if time in self.empty_values and suffix not in self.empty_values:
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid"
            )

        # Convert time and suffix to values
        time, suffix = int(time), int(suffix)
        twentyfour_hour = time + suffix

        # 12am and 12pm are kind of swapped (though 12pm is 24)
        if twentyfour_hour == 12:
            twentyfour_hour = 0
        elif twentyfour_hour == 24:
            twentyfour_hour = 12

        # Feed this into datetime.time and return
        return datetime.time(hour=twentyfour_hour)
