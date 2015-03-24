# Copyright (c) 2011, 2012, 2014, Aaron Madison
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.  

from django.conf import settings
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.forms.util import flatatt


class GoogleMapsAddressWidget(widgets.TextInput):
    "a widget that will place a google map right after the #id_address field"

    class Media:
        css = {'all': (settings.STATIC_URL + 'django_google_maps/css/google-maps-admin.css')}
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js',
            'https://maps.google.com/maps/api/js?sensor=false',
            settings.STATIC_URL + 'django_google_maps/js/google-maps-admin.js',
        )

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        html = '<input%s /><div class="map_canvas_wrapper"><div id="map_canvas"></div></div>'
        return mark_safe(html % flatatt(final_attrs))
