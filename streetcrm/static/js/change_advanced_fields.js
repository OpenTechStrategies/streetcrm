/*
  Copyright header!
*/

/*
Show and hide sets of fields depending on what kind of search is being
performed.
*/

function displayCorrectFields(){
    if ($("#id_search_model").val() == "event"){
        $(".participant_search_fields").hide();
        $(".action_search_fields").show();
    }
    else {
        $(".participant_search_fields").show();
        $(".action_search_fields").hide();
    }
}

function clearFilters(){
    // remove all autocompleted choices.  For some reason resetting the
    // form doesn't have the desired effect on these element, so we
    // simulate clicking on the span that removes each of them.
    $(".remove").trigger("click");
    // I had been resetting the form, but putting the fields into a
    // table seemed to break that and the only fields that were affected
    // by the reset were the start and end dates, anyway.
    $("#id_start_date").val("");
    $("#id_end_date").val("");
    $("#id_leader_stage").val("");
}

$(document).ready( function () {
    displayCorrectFields();
    $('#id_search_model').on("change", function() {
        displayCorrectFields();
    });
    $('#clear_filters_button').on("click", function(event) {
        event.preventDefault();
        clearFilters();
    });
});
