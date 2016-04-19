/*
 * Reload the page with the correct query when a new filter is chosen
 * from the dropdown.
 * 
*/

function reloadWithFilter(selected_obj) {
    // reload page with query from new selected value, without existing
    // query string
    var url = window.location.href;
    url = url.split('?');
    // get the new value
    var new_url = url[0] + $(selected_obj).val();
    // load this new url
    window.location.href = new_url;
}

$(document).ready( function () {
    // on change
    $(".filter_dropdown").on(
        "change",
        function() {
            reloadWithFilter(this);
        }
    );
});
