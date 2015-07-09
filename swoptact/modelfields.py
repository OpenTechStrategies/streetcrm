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

from django.db import models
from phonenumber_field import modelfields

from swoptact import formfields

class PhoneNumberField(modelfields.PhoneNumberField):

    def formfield(self, **kwargs):
        defaults = {
            "form_class": formfields.LocalPhoneNumberField,
        }
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)

class TwelveHourTimeField(models.TimeField):
    """ Twelve hour variant of django's TimeField """

    def formfield(self, **kwargs):
        # This can't go the standard route of letting kwargs override what we
        # set as the form_class key is overwritten in the autocomplete factory
        kwargs["form_class"] = formfields.TwelveHourTimeField

        # We also need to remove the widget as by default on admin ModelForms
        # it tries to use the special AdminTimeWidget.
        if "widget" in kwargs:
            del kwargs["widget"]
        return super(TwelveHourTimeField, self).formfield(**kwargs)
