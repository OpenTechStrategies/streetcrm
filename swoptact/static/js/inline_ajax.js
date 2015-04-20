/*
Eventually, this page should be able to do the following things:
(1) find the relevant participants for a given event and 
(2) display information about each of them, then 
(3) offer textboxes populated by values from that object onclick of an edit button
(4) save changes made via those text boxes
(5) remove a relationship between a person and an event, 
(6) add an entirely new person (really the same as (4)), 
(7) search for and 
(8) link an existing person to this event.

Currently it does only number two (2), of the above.
*/


/*****************
 *   OLD STUFF   *
 *****************/


function savePerson(person_object, event_id){
    //send info about an existing person to Jess's save endpoint
    var target_url = '/api/participants/'+person_object.id+'/';
    var person_parsed = JSON.stringify(person_object, null, 2);
    $.ajax({
        url: target_url,
        type: 'PUT',
        dataType: 'json',
        data: person_parsed,
        contentType: "application/json; charset=UTF-8",
        error: function(XMLHttpRequest, textStatus, errorThrown, result){
            alert(errorThrown);
        }, 
        success: function(result){
        }
    });
}


function getAvailableParticipants(){
    var event_id = document.getElementById('event_object_id').value;
    var url = '/api/events/'+event_id+'/available-participants';
    $.get(url,  function (result){
        var $select_available = $('<select id="available_participants_id">');
        for (i = 0; i < result.length; i++){
            $select_available.append('<option value="'+result[i].id+'">'+result[i].first_name+' '+result[i].last_name);
        }
        $('.module').append($select_available);
    });
}



function unlinkPerson(person_id){
    //send info about this person to Jess's delete endpoint
    var target_url = '/api/events/'+event_id+'/participants/'+person_id+'/';
    $.ajax({
        url: target_url,
        type: 'DELETE',
        success: function(result) {
            location.reload();
        }
    });
}

function linkPerson(event_id, person_id){
    var event_id = document.getElementById('event_object_id').value;
    var person_id = document.getElementById('available_participants_id').value;
    var target_url = '/api/events/'+event_id+'/participants/'+person_id+'/';
    $.ajax({
        url: target_url,
        type: 'POST',
        success: function(result) {
            location.reload();
        }
    });
}

/*
Loops through attendees and creates table rows to display and edit them
*/
function displayPerson(person, event){
    $('.editable').hide();
    var $tr = $('<tr>');
    $tr.append('<input class="attendee-id" type="hidden" value="'+person.id+'" />');
    var person_info = [person.first_name, person.last_name,
                       person.institution.name, person.phone_number,
                       person.address.number, person.address.direction,
                       person.address.name, person.address.type]; 
    $tr.append('<td>'+person.first_name+'<input type=text class="editable" value="'+person.first_name+'"></td>'); 
    $tr.append('<td>'+person.last_name+'<input type=text class="editable" value="'+person.last_name+'"></td>'); 
    $tr.append('<td>'+person.institution.name+'<input type=text class="editable" value="'+person.institution.name+'"></td>'); 

    $tr.append('<td>'+person.phone_number+'<input type=text class="editable" value="'+person.phone_number+'"></td>'); 

    var $address_td = $('<td>');
    $address_td.append(person.address.number+' '+person.address.direction+' '+person.address.name+' '+person.address.type);
    $address_td.append('<input type=text class="editable" size="5px"  value="'+person.address.number+'">');
    $address_td.append('<input type=text class="editable" size="3px" value="'+person.address.direction+'">');
    $address_td.append('<input type=text class="editable" size="15px" value="'+person.address.name+'">');
    $address_td.append('<input type=text class="editable" size="3px" value="'+person.address.type+'"></td>'); 
    $tr.append($address_td);
    var $btn_cell = $('<td>');
    $edit_btn = $('<input class="btn btn-info display_only" name="_edit" value="Edit" onclick="makePersonEditable('+person.id+')">');
    $btn_cell.append($edit_btn);
    var $save_btn = $('<input class="btn btn-success editable" name="_save" value="✓ Save" onclick="savePerson()">');
    $btn_cell.append($save_btn);
    $btn_cell.append('<input class="btn btn-warning editable" name="_cancel" value="✗ Cancel" onclick="makePersonDisplayOnly('+person.id+')">');
    $btn_cell.append('<input class="btn btn-danger display_only" name="_unlink" value="Remove attendee" onclick="unlinkPerson('+event+', '+person.id+')">');

    $tr.append($btn_cell);
    $('#attendees_table').append($tr);
    $('.editable').hide();
}


function getAttendees(){
    var event_id = document.getElementById('event_object_id').value;
    var url = '/api/events/'+event_id+'/participants';
    $.get(url,  function (people_list){
    for (i = 0; i < people_list.length; i++){
            displayPerson(people_list[i], event_id);
    }
    });
}


var example_person = {"email": "", "last_name": "Post", "id": 10, "address": {"__str__": "3100 93rd Street", "type": "St", "state": "IL", "id": 5, "apartment": null, "name": "93rd", "direction": "E", "city": "Chicago", "number": 3100, "zipcode": null}, "first_name": "Example", "secondary_phone": null, "institution": null, "phone_number": null};

function saveNewPerson(){
    var str = ( $("form").serialize());
    var str_arr = str.split("first");
    var person_string = "first"+str_arr[1];
    $('#testshow').text(person_string);
    $.post(
        '/api/participants/',
        ( $("form").serialize()),
        function (response){
            alert(response);
        }
    );
    
}


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
    // Revert and hide edit form
    revertEditRow(participant_id);
    hideParticipantEditRow(participant_id);

    // Hide and clear errors form
    hideParticipantErrorsRow(participant_id);
    clearErrors(participant_id);

    // Show display-only form
    showParticipantStaticRow(participant_id);
}


function revertEditRow(participant_id) {
    // TODO: base this on the filling system
    console.log("Imagine a world where we just reverted this row");
}


function clearErrors(participant_id) {
    // TODO: base this on the filling system
    console.log("DANGER WILMA ROBINSON!  INCOMPLETE!");
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
    fillErrorsRow(errors_row, participant, []);
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
}

/* Wipe out a row and add the hidden participant id input */
function resetRow(row, participant) {
    row.empty();
    row.append($(
        "<input/>",
        {"type": "hidden",
         "class": "participant-id",
         "value": participant.id}));
}

// Stubs, for now...
function fillStaticRow(row, participant) {
    resetRow(row, participant);

    appendSimpleText = function (text) {
        td_wrap = $("<td/>");
        p_wrap = $("<p/>");
        p_wrap.text(text);
        td_wrap.append(p_wrap);
        row.append(td_wrap);
    }

    appendSimpleText(participant.first_name);
    appendSimpleText(participant.last_name);
    appendSimpleText(participant.phone_number);
    if (participant.address) {
        appendSimpleText(participant.address.__str__);
    } else {
        appendSimpleText("");
    }

    // Now append the buttons...
    row.append('<td><button type="submit" class="btn btn-info participant-edit" name="_edit">✎ Edit</button> <button type="submit" class="btn btn-danger participant-unlink" name="_unlink">✘ Unlink</button></td>');
}

function fillEditRow(row, participant) {
    resetRow(row, participant);

    appendSimpleTextField = function (text) {
        td_wrap = $("<td/>");
        input_wrap = $("<input/>", {
            "class": "vTextField",
            "type": "text",
            "value": text});
        input_wrap.text(text);
        td_wrap.append(input_wrap);
        row.append(td_wrap);
    }

    appendSimpleTextField(participant.first_name);
    appendSimpleTextField(participant.last_name);
    appendSimpleTextField(participant.phone_number);
    if (participant.address) {
        appendSimpleTextField(participant.address.__str__);
    } else {
        appendSimpleTextField("");
    }

    // Now append the buttons...
    row.append('<td><button type="submit" class="btn btn-success participant-save" name="_save">✓ Save</button> <button type="submit" class="btn btn-warning participant-cancel" name="_cancel">✗ Cancel</button></td>');
}

function fillErrorsRow(row, participant, errors) {
    resetRow(row, participant);

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
    });
}


function setupParticipantCallbacks() {
    $("#participant-table").on(
        "click", "button.participant-edit",
        function(event) {
            event.preventDefault();
            makeParticipantEditable(getParticipantIdForRow($(this)));
        });

    $("#participant-table").on(
        "click", "button.participant-cancel",
        function(event) {
            event.preventDefault();
            cancelParticipantEdit(getParticipantIdForRow($(this)));
        });

    $(document).ready(function () {
        loadInitialAttendees();
    });

}


setupParticipantCallbacks();



// getAttendees(); 
// getAvailableParticipants();
//saveNewPerson();