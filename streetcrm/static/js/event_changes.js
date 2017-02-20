/* Show or hide the associated major action based on the value of the
 * "is this meeting part of a major action" checkbox. Note the unusual
 * technique of calling a javascript method by passing its name into
 * square brackets following the object.
*/
$(document).ready(function () {
    $("#id_major_action-wrapper").closest(".row")[$("#id_is_prep").is(":checked") ? "show" : "hide"]();
    $('#id_is_prep').on("click", function() {
        $("#id_major_action-wrapper").closest(".row")[$("#id_is_prep").is(":checked") ? "show" : "hide"]();
    });
});
