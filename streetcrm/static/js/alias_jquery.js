
$(document).ready(function() {
    if (typeof jQuery != 'undefined') {
        // jQuery is loaded, alias it to django.jQuery
        if (typeof(django) != 'undefined') {
            django.jQuery = $;
        }
    }
    else {
        console.log("ERROR: jQuery is not loaded and cannot be aliased to django.jQuery");
    }
});
