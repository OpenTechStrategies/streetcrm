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
from django.core import exceptions

def swoptact_login_required(func):
    """
    Decorator tests that a user is logged in.
    If the user is not authenticated it will raise the PermissionDenied
    exception.
    """

    def decorator(view_function):
        """ This is the decorator to be returned """
        def wrapped_view(request, *args, **kwargs):
            """ This pretneds to be the view to get at the request """
            if not request.user.is_authenticated():
                raise exceptions.PermissionDenied

            return view_function(request, *args, **kwargs)
        return wrapped_view

    return decorator(func)
