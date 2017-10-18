/*
 * Function for creating a temporary toast message display
 * from the supplied message
*/

/*
 * Splitting removal function so it can be added as a click handler
 * if someone wants to remove a message immediately.
 */
function removeToastMessage() {
    $("#toast").fadeOut(500, function () { $("#toast").remove(); });
}

/*
 * Add a disappearing toast message to the center of the page with a message.
 * Disappears after 3 seconds or on click.
 */
function toastMessage(message) {
    $("body").append("<div id='toast'>" + message + "</div>");
    $("#toast").fadeIn(500);
    $("#toast").on("click", removeToastMessage);
    setTimeout(function () {
        $("#toast").fadeOut(500, function () { $("#toast").remove(); });
    }, 3000);
}