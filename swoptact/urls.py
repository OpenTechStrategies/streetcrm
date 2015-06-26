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

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from swoptact import views

urlpatterns = patterns("",
    # Autocomplete app URLs
    url(r"^autocomplete/", include("autocomplete_light.urls")),

    # Admin site URLS
    url(r"^", include(admin.site.urls)),

    # API URLs
    url(r"^api/", include(patterns("",
        url(r"^participants/", include(patterns("",
            url(r"^$", views.CreateParticipantAPI.as_view(), name="api-create-participants"),
            url(r"^(?P<pk>\w+)/$", views.ParticipantAPI.as_view(), name="api-participants"),
        ))),
        url(r"^events/(?P<pk>\w+)/", include(patterns("",
            url(r"^participants/$", views.EventParticipantsAPI.as_view(), name="api-event-participants"),
            url(r"^available-participants/$", views.EventAvailableAPI.as_view(), name="api-event-available"),
            url(r"participants/(?P<participant_id>\w+)/$", views.EventLinking.as_view(), name="api-event-linking"),
        ))),
        url(r"^institutions/(?P<pk>\w+)/", include(patterns("",
            url(r"participants/(?P<participant_id>\w+)/$", views.ContactUnlinking.as_view(), name="api-unlink-contact"),
        ))),

        # This section covers endpoints for the current authenticated user
        url(r"^current/", include(patterns("",
            url(r"^available-tags/$", views.AvailableTagsAPI.as_view(), name="api-tags-available"),
        ))),
    ))),
    #autocomplete_light urls
    url(r'^autocomplete/', include('autocomplete_light.urls')),
)
