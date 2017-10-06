/*
 * Function for creating a temporary toast message display
 * from the supplied message
*/

function toastMessage(message) {
    $("body").append("<div id='toast'>" + message + "</div>");
    $("#toast").fadeIn(500);
    setTimeout(function () {
        $("#toast").fadeOut(500, function () { $("#toast").remove(); });
    }, 2500);
}