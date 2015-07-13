initialFormData = null;
formSubmitted = false;

function warnUnsaved() {
    // If the form is being processed, don't warn
    if (formSubmitted) {
        return;
    }   

    // Check if there is any unsaved fields and if so warm before leaving
    if (initialFormData != $("#fieldset-1").serialize()) {
        return "There's unsaved data, are you sure you want to leave.";
    }

    return;     
}


$(document).ready(function () {   
    // First populate the initial form data
    initialFormData = $("#fieldset-1").serialize(); 

    // Setup callbacks.
    $("form").submit(function () {
        formSubmitted = true;
    });
    window.onbeforeunload = warnUnsaved;
});
