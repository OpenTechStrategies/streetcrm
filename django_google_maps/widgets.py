# No copyright header was originally placed in this file, but it was
# sourced from Aaron Madison in 2015.  See
# https://github.com/madisona/django-google-maps

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
        html = u'<input%s /><div class="map_canvas_wrapper"><div id="map_canvas"></div></div>'
        return mark_safe(html % flatatt(final_attrs))
