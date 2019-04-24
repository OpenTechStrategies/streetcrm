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

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.views.generic import TemplateView

from streetcrm import views, admin

urlpatterns = [
    # Autocomplete app URLs
    # url(r"^autocomplete/", include("dal.urls")),

    # Admin site URLs
    url(r"^", admin.site.urls),

    # Help page
    url(r"^help/", TemplateView.as_view(template_name="admin/help.html"), name="help"),

    # Import URLs
    url(r"^import/", include([
        url(r"^events/$", views.EventImport.as_view(), name="import-events"),
        url(r"^events/(?P<pk>\w+)/participants/$",
            views.EventParticipantsImport.as_view(),
            name="import-event-participants"
        ),
        url(r"^participants/$", views.ParticipantImport.as_view(), name="import-participants")
    ])),

    # API URLs
    url(r"^api/", include([
        url(r"^participants/", include([
            url(r"^$", views.CreateParticipantAPI.as_view(), name="api-create-participants"),
            url(r"^(?P<pk>\w+)/$", views.ParticipantAPI.as_view(), name="api-participants"),
            url(r"^([\w-]+)/$", views.ParticipantAPI.as_view(), name="api-participants"),
            url(r"^contact/(?P<pk>\w+)/$", views.ContactParticipantAPI.as_view(), name="api-participants"),
        ])),
        url(r"^contacts/", views.CreateContactAPI.as_view(), name="api-create-contacts"),
        url(r"^events/(?P<pk>\w+)/", include([
            url(r"^participants/$", views.EventParticipantsAPI.as_view(), name="api-event-participants"),
            url(r"^available-participants/$", views.EventAvailableAPI.as_view(), name="api-event-available"),
            url(r"participants/(?P<participant_id>\w+)/$", views.EventLinking.as_view(), name="api-event-linking"),
        ])),
        url(r"^institutions/(?P<pk>\w+)/", include([
            url(r"^contacts/$", views.InstitutionContactsAPI.as_view(), name="api-institution-contacts"),
            url(r"contacts/(?P<participant_id>\w+)/$", views.ContactLinking.as_view(), name="api-contact-linking"),
        ])),

        # This section covers endpoints for the current authenticated user
        url(r"^current/", include([
            url(r"^available-tags/$", views.AvailableTagsAPI.as_view(), name="api-tags-available"),
        ])),
    ])),
    #dal urls
    # url(r'^autocomplete/', include('dal.urls')),

]
