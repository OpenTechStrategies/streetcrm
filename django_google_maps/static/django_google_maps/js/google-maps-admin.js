/*
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


Integration for Google Maps in the django admin.

How it works:

You have an address field on the page.
Enter an address and an on change event will update the map
with the address. A marker will be placed at the address.
If the user needs to move the marker, they can and the geolocation
field will be updated.

Only one marker will remain present on the map at a time.

This script expects:

<input type="text" name="address" id="id_address" />
<input type="text" name="geolocation" id="id_geolocation" />

<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>

*/

function googleMapAdmin() {

    var geocoder = new google.maps.Geocoder();
    var map;
    var marker;

    var self = {
        initialize: function() {
            var lat = 0;
            var lng = 0;
            var zoom = 2;
            self.codeAddress();
            var latlng = new google.maps.LatLng(lat,lng);
            var myOptions = {
              zoom: zoom,
              center: latlng,
              mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

            $("#id_address").change(function() {self.codeAddress();});
        },

        getExistingLocation: function() {
            var geolocation = $("#id_geolocation").val();
            if (geolocation) {
                return geolocation.split(',');
            }
        },

        codeAddress: function() {
            var address_start = $("#id_address option:selected").text();
            var address = address_start + '+Chicago+IL';
            geocoder.geocode({'address': address}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    var latlng = results[0].geometry.location;
                    map.setCenter(latlng);
                    map.setZoom(18);
                    map.setMapTypeId(google.maps.MapTypeId.ROADMAP);

                    self.setMarker(latlng);
                    self.updateGeolocation(latlng);
                } else {
                    alert("Geocode was not successful for the following reason: " + status);
                }
            });
        },

        setMarker: function(latlng) {
            if (marker) {
                self.updateMarker(latlng);
            } else {
                self.addMarker({'latlng': latlng, 'draggable': true});
            }
        },

        addMarker: function(Options) {
            marker = new google.maps.Marker({
                map: map,
                position: Options.latlng
            });

            var draggable = Options.draggable || false;
            if (draggable) {
                self.addMarkerDrag(marker);
            }
        },

        addMarkerDrag: function() {
            marker.setDraggable(true);
            google.maps.event.addListener(marker, 'dragend', function(new_location) {
                self.updateGeolocation(new_location.latLng);
            });
        },

        updateMarker: function(latlng) {
            marker.setPosition(latlng);
        },

        updateGeolocation: function(latlng) {
            $("#id_geolocation")
                .val(latlng.lat() + "," + latlng.lng())
                .trigger('change');
        }
    }

    return self;
}

$(document).ready(function() {
    var googlemap = googleMapAdmin();
    googlemap.initialize();
});