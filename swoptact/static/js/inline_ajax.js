/*
This page governs the sign-in sheet on the change event form.  It includes
functions to:
(1) find the relevant participants for a given event
(2) display information about each of them
(3) edit textboxes populated by values from that object
(4) save changes made via those text boxes
(5) unlink a person from an event
(6) add an entirely new person (really the same as (4))
(7) search available participants
(8) link an existing person to this event.

*/



/*****************
 *   NEW STUFF   *
 *****************/

// Hide and show stuff

function getParticipantStaticRow(participant_id) {
    return $("#participant-static-" + participant_id);
}
function hideParticipantStaticRow(participant_id) {
    getParticipantStaticRow(participant_id).hide();
}
function showParticipantStaticRow(participant_id) {
    getParticipantStaticRow(participant_id).show();
}


function getParticipantEditRow(participant_id) {
    return $("#participant-edit-" + participant_id);
}
function hideParticipantEditRow(participant_id) {
    getParticipantEditRow(participant_id).hide();
}
function showParticipantEditRow(participant_id) {
    getParticipantEditRow(participant_id).show();
}


function getParticipantErrorsRow(participant_id) {
    return $("#participant-errors-" + participant_id);
}
function hideParticipantErrorsRow(participant_id) {
    getParticipantErrorsRow(participant_id).hide();
}
function showParticipantErrorsRow(participant_id) {
    getParticipantErrorsRow(participant_id).show();
}


function getEventId() {
    return document.getElementById('event_object_id').value;
}


/* Handle the "edit" button for a participant row. */
function makeParticipantEditable(participant_id) {
    // TODO: Copy data into the edit form

    // Hide display-only form
    hideParticipantStaticRow(participant_id);
    // Show edit form
    showParticipantEditRow(participant_id);
}

/* Handle the "cancel" button for a participant edit-in-progress. */
function cancelParticipantEdit(participant_id) {
    // Oh, this is the add new one... well, we don't need to switch
    // back to a static view.  Just dump it.
    if (participant_id == "") {
        unlinkParticipant(participant_id);
    }

    // TODO: Do a *real* revert of the data here!
    //// Revert and hide edit form
    // revertEditRow(participant_id);
    hideParticipantEditRow(participant_id);

    // Hide and clear errors form
    hideParticipantErrorsRow(participant_id);
    clearErrors(participant_id);

    // Show display-only form
    showParticipantStaticRow(participant_id);
}


function revertEditRow(participant_id) {
    // TODO: base this on the filling system
}


function clearErrors(participant_id) {
    fillErrorsRow(getParticipantErrorsRow(participant_id), participant_id, []);
}


function getParticipantIdForRow(jq_element) {
    // Take a jquery element for any member of a participant row
    // and extract the participant id (returned as a string)
    return jq_element.parents("tr").children(".participant-id")[0].value;
}


/* Insert a participant into the DOM.

Here, the participant is a json object, as fetched from the API. */
function insertParticipant(participant) {
    // TODO: Insert the participant into a hashmap for later reference?
    //   (eg, if canceling an edit...)

    // Construct and insert static row
    // -------------------------------
    var static_row = $(
        "<tr />",
        {"class": "form-row participant-static",
         "id": "participant-static-" + participant.id});
    fillStaticRow(static_row, participant);
    $("#participant-table tbody").append(static_row);
    // Construct and insert error row (empty for now)
    // ----------------------------------------------
    var errors_row = $(
        "<tr />",
        {"class": "form-row participant-errors",
         "id": "participant-errors-" + participant.id});
    errors_row.hide()
    fillErrorsRow(errors_row, participant.id, []);
    $("#participant-table tbody").append(errors_row);

    // Construct and insert edit row
    // -----------------------------
    var edit_row = $(
        "<tr />",
        {"class": "form-row participant-edit",
         "id": "participant-edit-" + participant.id});
    fillEditRow(edit_row, participant);
    edit_row.hide()
    $("#participant-table tbody").append(edit_row);

    // Special hack for the "new" participant: turn on autocomplete for this row
    if (participant.id === "") {
        turnOnAutocomplete(edit_row);
    }
}


function turnOnAutocomplete(edit_row) {
    console.log("Turning on autocomplete");

    // Hook in the autocomplete function
    edit_row.find("input.name").autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/autocomplete/ContactAutocomplete/",
                datatype: "html",
                data: {
                    q: request.term
                },
                success: function(data) {
                    var json_data = $.map(
                        $.makeArray(data),
                        function(elt) {
                            return {
                                "value": $(elt).attr("data-value"),
                                "label": $(elt).text()}});
                    // massage data or in the select func?
                    response(json_data);
                }});
        },
        select: function(event, ui) {
            if (ui.item) {
                var participant_id = ui.item.value
                // Remove this row
                cancelParticipantEdit("");
                // Insert the participant and make them immediately editable
                linkParticipant(participant_id, true);
            }
        }
    });
}

/* Wipe out a row and add the hidden participant id input */
function resetRow(row, participant_id) {
    row.empty();
    row.append($(
        "<input/>",
        {"type": "hidden",
         "class": "participant-id",
         "value": participant_id}));
}

// Stubs, for now...
function fillStaticRow(row, participant) {
    resetRow(row, participant.id);

    appendSimpleText = function (text) {
        td_wrap = $("<td/>");
        p_wrap = $("<p/>",
                   {"style": "font-size: 18"});
        p_wrap.text(text);
        td_wrap.append(p_wrap);
        row.append(td_wrap);
    }

    appendSimpleText(participant.name);
    if (participant.institution) {
        appendSimpleText(participant.institution.name);
    } else {
        appendSimpleText("");
    }
    if (participant.primary_phone) {
        appendSimpleText(participant.primary_phone);
    } else {
        appendSimpleText("");
    }

    // Now append the buttons...
    row.append('<td><button type="submit" class="btn participant-edit" name="_edit">✎ Edit</button> <button type="submit" class="btn participant-unlink" name="_unlink">✘ Undo</button></td>');
}

function fillEditRow(row, participant) {
    resetRow(row, participant.id);
    appendSimpleTextField = function (text, class_identifier) {
        td_wrap = $("<td/>");
        input_wrap = $("<input/>", {
            "class": "vTextField " + class_identifier,
            "type": "text",
            "id": "edit-" + class_identifier + "-" + participant.id,
            "value": text});
        input_wrap.text(text);
        td_wrap.append(input_wrap);
        row.append(td_wrap);
    }

    appendSimpleTextField(participant.name, "name");
    if (participant.institution) {
        appendSimpleTextField(participant.institution.name, "institution");
    } else {
        appendSimpleTextField("", "institution");
    }
    appendSimpleTextField(participant.primary_phone, "primary-phone");
    // Now append the buttons...
    row.append('<td><button type="submit" class="btn participant-save" name="_save">✓ Done</button> <button type="submit" class="btn participant-cancel" name="_cancel">✗ Cancel</button></td>');
}


function fillErrorsRow(row, participant_id, errors) {
    resetRow(row, participant_id);

    var td = $('<td colspan="5" />');

    if (errors.length > 0) {
        td.append($("<p><i>Errors were found in the entry below...</i></p>"));
    }

    errors.forEach(function(error_msg) {
        warning_div = $('<div class="alert alert-danger" />');
        warning_div.text(error_msg);
        td.append(warning_div);
    });

    row.append(td);
}


function loadInitialAttendees() {
    var event_id = getEventId();
    var url = '/api/events/'+event_id+'/participants';
    $.get(url, function (people_list) {
        for (i = 0; i < people_list.length; i++){
            insertParticipant(people_list[i]);
        }
    }, "json");
}


// The function that both adds the participant on the backend and links
// on the frontend
function linkParticipant(participant_id, make_editable) {
    var url = '/api/events/'+getEventId()+'/participants/'+participant_id+"/";
    $.post(url, function (result) {
        $.get('/api/participants/'+participant_id+'/',
              function (participant) {
                  insertParticipant(participant);
                  if (make_editable) {
                      makeParticipantEditable(participant_id);
                  }
              }, 'json');
    }, "json");
}


function backToPreLinkParticipants() {
    $("#add-new-participant-btn").show();
    $('#available-participants-select').hide();
    $("#cancel-link-existing-btn").hide();
    $("#select-existing-participant-btn").hide();
}

function unlinkParticipant(participant_id){
    var removeRows = function () {
        getParticipantStaticRow(participant_id).remove();
        getParticipantEditRow(participant_id).remove();
        getParticipantErrorsRow(participant_id).remove();
    }

    // An empty, pre-saved new participant.
    if (participant_id == "") {
        removeRows();
        return false;
    }

    var event_id = getEventId();
    var target_url = '/api/events/'+event_id+'/participants/'+participant_id+'/';
    $.ajax({
        url: target_url,
        type: 'DELETE',
        success: removeRows});
}


// Save all rows that are currently being edited
//
// We have to rely on jquery telling us what's visible or not
// since we don't have any other markers of what's in editing mode
function saveAllEditing() {
    // Find all currently being edited rows and the participant thereof,
    // then save
    $("tr.participant-edit:visible input.participant-id").each(
        function(index) {
            saveParticipant(this.value, false);
        });
}


function addNewParticipant() {
    saveAllEditing();

    if (getParticipantEditRow("").length > 0) {
        // We already have an empty participant in progress
        return false;
    }

    // NOTE: Not all our code is really set up to handle
    // passing in a mostly empty object as a participant :\
    // This is a hack!
    // Seems to work tho
    insertParticipant({"id": ""});
    hideParticipantStaticRow("");
    showParticipantEditRow("");
}


/*
 takes a participant object and returns a participant object filled with new
 values from the input fields in that participant's row
 */
function updateParticipant(participant){
    if (participant.id){
        var edit_input = $('#participant-edit-'+participant.id);
    }
    else{
        var edit_input = $('#participant-edit-');
    }
    var text_inputs = (edit_input.find(".vTextField"));
    // array will be name, phone_number, address as long as our
    // UI columns stay the same
    participant.name = text_inputs[0].value;
    participant.primary_phone = text_inputs[2].value;
    return participant;
}

/*
  helper function to find the correct rows and fill them using other functions,
  after a participant is updated
*/
function recreateRows(participant){
    fillEditRow(getParticipantEditRow(participant.id),
                participant);
    fillErrorsRow(getParticipantErrorsRow(participant.id),
                  participant.id, []);
    fillStaticRow(getParticipantStaticRow(participant.id),
                  participant);
    hideParticipantEditRow(participant.id);
    hideParticipantErrorsRow(participant.id);
    showParticipantStaticRow(participant.id);
}


function saveParticipant(participant_id, submit_flag) {
    if (participant_id != "empty" && participant_id != ""){
        $.get('/api/participants/'+participant_id+'/',
              function (participant) {
                  new_participant = updateParticipant(participant);
                  data = JSON.stringify(new_participant);
                  $.ajax({
                      url: '/api/participants/'+participant_id+'/',
                      data: data,
                      type: 'PUT',
                      error: function (response) {
                          // TODO: This is where we're supposed to fill in the
                          //   errors fow
                          console.log(response)
                      },
                      success: function (response) {
                          recreateRows(response);
                          if (submit_flag){
                              $("#event_form").submit();
                          }
                      },
                      dataType: 'json'
                  });
              }, 'json');
    } else {
        empty_participant = {};
        new_participant = updateParticipant(empty_participant);
        data = JSON.stringify(new_participant);
        $.ajax({
            url: '/api/participants/',
            data: data,
            type: 'POST',
            error: function (response) {console.log(response)},
            success: function (response) {
                var url = '/api/events/'+getEventId()+'/participants/'+response.id+"/";
                $.post(url, function (result) {
                    $.get('/api/participants/'+response.id+'/',
                          function (participant) {
                              unlinkParticipant("");
                              insertParticipant(participant);
                              if (submit_flag){
                                  $("#event_form").submit();
                              }
                          }, 'json');
                }, "json");
                
            },
            dataType: 'json'
        });
    }
}

function setupParticipantCallbacks() {
    //keep track of row(s) in the middle of being edited
    var rows_editing = [];
    $("#participant-table").on(
        "click", "button.participant-edit",
        function(event) {
            rows_editing.push(getParticipantIdForRow($(this)));
            event.preventDefault();
            makeParticipantEditable(getParticipantIdForRow($(this)));
        });

    $("#participant-table").on(
        "click", "button.participant-unlink",
        function(event) {
            event.preventDefault();
            unlinkParticipant(getParticipantIdForRow($(this)));
        });

    $("#participant-table").on(
        "click", "button.participant-cancel",
        function(event) {
            var index = rows_editing.indexOf(getParticipantIdForRow($(this)));
            if (index > -1){
                rows_editing.splice(index, 1);
            }
            event.preventDefault();
            cancelParticipantEdit(getParticipantIdForRow($(this)));
        });

    $("#participant-table").on(
        "click", "button.participant-save",
        function(event) {
            var index = rows_editing.indexOf(getParticipantIdForRow($(this)));
            if (index > -1){
                rows_editing.splice(index, 1);
            }
            event.preventDefault();
            saveParticipant(getParticipantIdForRow($(this)), false);
        });

    $("#add-new-participant-btn").on(
        "click",
        function(event) {
            event.preventDefault();
            addNewParticipant();
            // addNewParticipant saves all open rows, so we empty the existing
            // array of rows being edited.
            rows_editing = [];
            // this case still needs to be handled correctly
            rows_editing.push('empty');
        });

    $("#test_submit").on(
        "click",
        function (event) {
            if (rows_editing[0]){
                for (j = 0; j < rows_editing.length; j++) {
                    if (j == (rows_editing.length - 1) ) {
                        //for last value, pass the flag that says "and submit"
                        saveParticipant(rows_editing[j], true);
                    }
                    else{
                        saveParticipant(rows_editing[j], false);
                    }
                }
            }
            else{
                $("#event_form").submit();
            }
        });

    $(document).ready(function () {
        loadInitialAttendees();
    });



}


setupParticipantCallbacks();
