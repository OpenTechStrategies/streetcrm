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

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from swoptact import views

urlpatterns = patterns("",
    # Admin site URLS
    url(r"^", include(admin.site.urls)),

    # API URLs
    url(r"^api/", include(patterns("",
        url("^participants/", include(patterns("",
            url("^$", views.AllParticipantsAPI.as_view(), name="api-all-participants"),
            url("^(?P<pk>\w+)/$", views.ParticipantAPI.as_view(), name="api-participants"),
        ))),
    ))),
)
