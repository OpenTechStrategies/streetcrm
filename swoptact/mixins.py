# SWOPTACT is a list of contacts with a history of their event attendance
# Copyright (C) 2015  Open Tech Strategies, LLC
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

from django.core import urlresolvers
from django.conf.urls import patterns, url
from django.shortcuts import render_to_response
from django.forms.models import modelform_factory

from autocomplete_light import widgets as dacl_widgets

class SignInSheetAdminMixin:
    """
    Provides a special case sign in sheet view

    This will be inherited by ParticipantAdmin and is only a separate
    class to make it easier to think about. You should prefix your
    attributes and method names with "sheet_" to avoid conflict.
    """
    sheet_template = "admin/sign_in_sheet.html"


    def get_urls(self, *args, **kwargs):
        # Get the URLs of the superclass.
        urls = super(SignInSheetAdminMixin, self).get_urls(*args, **kwargs)

        # Define the sign in sheet URL
        sheet_view = self.admin_site.admin_view(self.sheet_view)
        sheet_url = patterns("",
            url(r"sign-in-sheet/$", sheet_view, name="sign-in-sheet"),
        )

        return sheet_url + urls


    def sheet_view(self, request):
        """ View for the sign in sheet """
        # To prevent circular imports keep this here.
        from swoptact import models

        return render_to_response(self.sheet_template, {
            "opts": self.model._meta,
            "event_form": modelform_factory(
                model=Event,
                exclude=("description", "participants", "is_prep")
            ),
            "participant_form": modelform_factory(
                model=models.Participant,
                exclude=("address", "secondary_phone", "email")
            ),
            "institution_form": modelform_factory(
                model=models.Institution,
                exclude=tuple()
            ),
        })


class AdminURLMixin:
    """ Provides Django's Admin URLs for a model managed by the admin app """

    def __admin_url(self, url):
        """
        Finds the Admin url for a URL

        This will only work for the URLs which are called on a object rather
        than the model (e.g. not adding) this also needs to be for URLs which
        take the ID of the object. If you wanted to extend this in the future
        you would have to look up the ContentType yourself instead of using the
        _meta information prvovided by initialised objects.
        """
        url_name = "admin:{app_label}_{model_name}_{url}".format(
            app_label=self._meta.app_label,
            model_name=self._meta.model_name,
            url=url
        )
        return urlresolvers.reverse(url_name, args=(self.pk,))

    @property
    def admin_change_url(self):
        """ Admin page to edit the object """
        return self.__admin_url("change")

    @property
    def admin_delete_url(self):
        """ Admin page to delete the object """
        return self.__admin_url("delete")

    @property
    def admin_history_url(self):
        """ Admin page to see the history of the object """
        return self.__admin_url("history")