/*
  Copyright header!
*/

/*
Show and hide sets of fields depending on what kind of search is being
performed.
*/

$(document).ready( function () {
    // only 
    if ($("#id_search_model").val() == "participant"){
        $("#participant_search_fields").show();
        $("#action_search_fields").hide();
    }
    else{
        $("#participant_search_fields").hide();
        $("#action_search_fields").show();
    }
    $('#id_search_model').on("change", function() {
        if ($("#id_search_model").val() == "event"){
            $("#participant_search_fields").hide();
            $("#action_search_fields").show();
        }
        else {
            $("#participant_search_fields").show();
            $("#action_search_fields").hide();
        }
    });
});
