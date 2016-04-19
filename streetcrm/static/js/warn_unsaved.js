initialFormData = null;
formSubmitted = false;

function warnUnsaved() {
    // If the form is being processed, don't warn
    if (formSubmitted) {
        return;
    }

    // Check if there are any unsaved fields and if so warn before leaving
    if (initialFormData != $("#fieldset-1").serialize()) {
        return "You have entered data without saving it. Are you sure you want to leave this page?";
    }

    return;
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
