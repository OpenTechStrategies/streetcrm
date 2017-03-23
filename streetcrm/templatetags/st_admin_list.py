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

from django.template import Library
from django.contrib.admin.templatetags import admin_list
from django.contrib.admin.templatetags.admin_modify import *
from django.contrib.admin.templatetags.admin_modify import submit_row as original_submit_row


register = Library()

@register.inclusion_tag("admin/change_list_results.html")
def smart_result_list(cl):
    """
    Displays the headers and data list together

    If there is only column the headers are not displayed as it is usually
    clear what is being displayed. This change comes from issue #67, if you
    want to always display the header use Django's `result_list`.
    """
    result_list_context = admin_list.result_list(cl)

    # If there is one or less headers remove them.
    if len(result_list_context["result_headers"]):
        del result_list_context["result_headers"]
    return result_list_context

# Thanks to inspiration from http://stackoverflow.com/a/13106661/6005068
@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def submit_row(context):
    """
    Takes the default submit_row context.  Override this context in
    order to add the new property "can_archive." Return the updated
    context.
    """
    ctx = original_submit_row(context)
    ctx.update({
        'can_archive': context.get('can_archive'),
        })                                                                  
    return ctx 
