formSubmitted = false;

function warnUnsaved() {
    // If the form is being processed, don't warn
    if (formSubmitted) {
        return;
    }

    // Find the API URL
    var pathname = window.location.pathname.split("/");

    // Find the model name from the pathname (APIs use the plural version)
    var modelname = pathname[1] + 's';

    // Find the object ID
    var objectID = pathname[2];

    var apiURL = "/api/" + modelname + "/" + objectID + "/";

    // Check if there are any unsaved fields and if so warn before leaving
    var unsavedData = false;

    $.get(apiURL, function(data) {
        $.each(data, function (field, value) {
            var pageValue = $("#id_" + field).val();
            if (value != field()) {
                unsavedData = true;
            };
        });
    }, "json");

    if (unsavedData) {
        return "You have entered data without saving it. Are you sure you want to leave this page?";
    }
}


$(document).ready(function () {
    // First populate the initial form data
    initialFormData = $("#fieldset-1").serialize();

    // Set up callbacks.
    $("form").submit(function () {
        formSubmitted = true;
    });
    window.onbeforeunload = warnUnsaved;
});
