function chooseSearchForm() {
    // Initially we want to hide all of the search forms then just show the desired form
    $("#id_participant_search_form").css("display", "none");
    $("#id_institution_search_form").css("display", "none");
    $("#id_event_search_form").css("display", "none");

    // Get the selected model
    var selectedModel = $("#id_search_model option:selected").val()

    // Find the form for the model
    var formObj = $("#id_" + selectedModel + "_search_form");

    // Remove the display: none from it.
    formObj.css("display", "");
}

$(document).ready(function () {
    // Set up callbacks.
    $("#id_search_model").change(chooseSearchForm);

    // Call chooseSearchForm to get the form to display on page load
    chooseSearchForm();
});
