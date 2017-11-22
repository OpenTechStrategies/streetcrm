/*
 * Function for creating a temporary toast message display
 * from the supplied message
*/

// Setting variable to hold the timeout ID so it can be cleared
var TOAST_TIMEOUT;

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
    if (TOAST_TIMEOUT) clearTimeout(TOAST_TIMEOUT);
    $("#toast").remove();
    $("body").append("<div id='toast'>" + message + "</div>");
    $("#toast").fadeIn(500);
    $("#toast").on("click", removeToastMessage);
    TOAST_TIMEOUT = setTimeout(function () {
        $("#toast").fadeOut(500, function () { $("#toast").remove(); });
    }, 3000);
}