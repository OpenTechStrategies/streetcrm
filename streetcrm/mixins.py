# StreetCRM is a list of contacts with a history of their event attendance
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

from django import http
from django.db import transaction
from django.contrib import messages
from django.core import urlresolvers
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.forms.models import modelform_factory
from django.utils.translation import ugettext as _
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

from autocomplete_light import widgets as dacl_widgets

import datetime
from datetime import datetime
import csv

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
        from streetcrm import models

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

class AdminExportMixin:
    """
    Admin mixin for exporting models as CSV

    This provides both the url for the model, as well as working with the
    changelist_view to make the export button show up.  Requires the Admin
    to provide the headers/fields for the export via self.export_header.
    """

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["export_link"] = "admin:%s_%s_export" % self.url_info
        return super(AdminExportMixin, self).changelist_view(request, extra_context)

    def get_urls(self, *args, **kwargs):
        urls = super(AdminExportMixin, self).get_urls(*args, **kwargs)
        urls.insert(
            0,
            url(r"^export/$", self.export_as_csv, name="%s_%s_export" % self.url_info)
        )
        return urls

    def export_as_csv(self, request):
        from streetcrm import models
        from streetcrm import admin

        response = http.HttpResponse(content_type='text/csv')
        filetime = datetime.now()

        filename=self.model.__name__ + "List-" + str(filetime.year) + "-" + str(filetime.month) + "-" + str(filetime.day) + "-" + str(filetime.hour) + str(filetime.minute) + str(filetime.second) + ".csv"
        response['Content-Disposition'] = 'attachment; filename='+filename
        writer = csv.writer(response)

        admin.STREETCRMAdminSite.export_results(writer, self.export_header, self.model.objects.all())

        return response

class AdminArchiveMixin:
    """
    Admin mixin for archivable ModelAdmins

    This prevents the delete confirmation page as everything is archived and the
    ability to rollback to the unarchived version is possible.
    """

    @property
    def url_info(self):
        return self.model._meta.app_label, self.model._meta.model_name

    def get_urls(self, *args, **kwargs):
        urls = super(AdminArchiveMixin, self).get_urls(*args, **kwargs)
        urls.insert(
            0,
            url(r"^(.+)/unarchive/$", self.unarchive_view, name="%s_%s_unarchive" % self.url_info)
        )
        urls.insert(
            0,
            url(r"^(.+)/archive/$", self.archive_view, name="%s_%s_archive" % self.url_info),
        )
        return urls

    def unarchive_view(self, request, object_id, *args, **kwargs):
        # Lookup the object
        obj = self.model.objects.get(pk=object_id)
        obj.unarchive()

        # Redirect back to change form.
        change_form = reverse("admin:%s_%s_change" % self.url_info, args=(object_id,))
        return http.HttpResponseRedirect(change_form)

    def queryset(self, request):
        return self.model.objects.unarchive()

    @transaction.atomic
    def archive_view(self, request, object_id, *args, **kwargs):
        # If this is submitted with as a "POST" request then django
        # assumes the confirmation has occured.

        # This won't work since each model will have a different
        # permission
        if not request.user.has_perm("streetcrm.archive_participant"):
            print("DEBUG: permissions problem")
            raise exceptions.PermissionDenied
        
        request.POST = {"post": True}
        obj = self.model.objects.get(pk=object_id)
        obj.archive()
        return self.response_archive(request, obj.name, obj.id)
    

    def response_archive(self, request, obj_display, obj_id):
        opts = self.model._meta

        self.message_user(
            request,
            _("The {name} \"{obj}\" was archived successfully.").format(
                name=opts.verbose_name,
                obj=obj_display
            ),
            messages.SUCCESS
        )

        if self.has_change_permission(request, None):
            url_name = "admin:%s_%s_changelist" % self.url_info
            post_url = urlresolvers.reverse(
                url_name,
                current_app=self.admin_site.name
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts},
                post_url
            )
        else:
            post_url = urlresolvers.reverse(
                "admin:index",
                current_app=self.admin_site.name
            )
        return http.HttpResponseRedirect(post_url)
