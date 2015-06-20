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

import phonenumbers

from django.core import validators
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
