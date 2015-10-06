/*
 * Add toggling to the sections of the missing data report, and show
 * them as closed by default.
*/


$(document).ready( function() {
    // hide results by default
    $(".results").hide();
    // get headers
    $("h2").on("click", function() {
        // on click of each, toggle the next results class div (show the
        // relevant results)
        $(this).next(".results").toggle();
    });

});
