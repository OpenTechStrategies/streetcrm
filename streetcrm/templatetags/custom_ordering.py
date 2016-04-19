# Inspired by https://djangosnippets.org/snippets/2613/
# Author: Harmanas S. C.
#
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
from collections import OrderedDict

from django import template
from django.conf import settings
from django.template.base import Node

register = template.Library()

class OrderedContext(dict):
    """ Wrapper context dict to provide comparison operators """

    def __init__(self, *args, **kwargs):
        super(OrderedContext, self).__init__(*args, **kwargs)

    def _index(self, item):
        """
        Find the index of the items "name" entry

        If there is no "name" entry or the "name" entry is not in self.ORDERING
        then it will raise a ValueError, otherwise it will return the index
        of the item in self.ORDERING
        """
        return self.ORDERING.index(item.get("name"))

    def __lt__(self, other):
        """
        Check if self is less than other

        If self is less than other than True is returned, otherwise False is
        returned. If the element isn't found in self.ORDERING then other is
        considered less than self."""
        try:
            return self._index(self) < self._index(other)
        except ValueError:
            return True

    def __gt__(self, other):
        """
        Check if self is greater than other

        If self is greater than other than True is returned, otherwise False is
        returned. If the element isn't found in self.ORDERING then other is not
        considered greater than self."""
        try:
            return self._index(self) > self._index(other)
        except ValueError:
            return False

class AppOrderedContext(OrderedContext):
    """ Dictionary for apps with comparison """

    def __init__(self, *args, **kwargs):
        self.ORDERING = list(OrderedDict(settings.ADMIN_ORDERING).keys())
        super(AppOrderedContext, self).__init__(*args, **kwargs)

class ModelOrderedContext(OrderedContext):
    """ Dictionary for models with comparison """

    def __init__(self, app, *args, **kwargs):
        self.ORDERING = OrderedDict(settings.ADMIN_ORDERING).get(app, [])
        super(ModelOrderedContext, self).__init__(*args, **kwargs)

class AppOrderNode(Node):
    """
        Reorders the app_list and child model lists on the admin index page.
    """
    def render(self, context):
        # First we need to put the apps in OrderedContext
        apps = [AppOrderedContext(app) for app in context["app_list"]]
        apps.sort()

        for app in apps:
            # Get the name of the app
            name = app["name"]
            models = app["models"]

            # Convert each model context to OrderedContext so we can sort them
            models = [ModelOrderedContext(name, ctx) for ctx in models]
            models.sort()
            app["models"] = models

        context["app_list"] = apps
        return ""

def app_order(parser, token):
    return AppOrderNode()
var = register.tag(app_order)
