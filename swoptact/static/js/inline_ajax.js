/*
Eventually, this page should be able to do the following things:
(1) find the relevant participants for a given event and (2) display 
information about each of them, then (3) offer textboxes populated by values
from that object onclick of an edit button and (4) save changes made via those
text boxes by sending the new information as a JSON object to an endpoint
elsewhere.
It should also (5) remove a relationship between a person and an event, (6) add
an entirely new person (really the same as (4)), and (7) search for and (8) link
an existing person to this event.

Currently it does only number two (2), of the above.
*/


function editPerson(){
    $('.editable').toggle();
    $('.display_only').toggle();
}

function savePerson(){
    //send info about an existing person to Jess's save endpoint
}

function unlinkPerson(event_id, person_id){
    //send info about this person to Jess's delete endpoint
    //this doesn't work yet
    var target_url = '/api/events/'+event_id+'/participants/'+person_id+'/';
    $.ajax({
        url: target_url,
        type: 'DELETE',
        success: function(result) {
        }
    });
}

/*
Loops through attendees and creates table rows to display and edit them
*/
function displayPerson(person){
    $('.editable').hide();
//    $('#attendees_table').append('<tr></tr>');
    $tr = $('<tr>');
    var person_info = [person.first_name, person.last_name,
                            person.phone_number, person.institution.name];
    for	(index = 0; index < person_info.length; index++) {
        $tr.append('<td>'+person_info[index]+'<input type=text class="editable"></td>');
    }
    $tr.append('<td>');
    $edit_btn = $('<input class="btn btn-info display_only" name="_edit" value="Edit" onclick="editPerson()">');
    $tr.append($edit_btn);
    $tr.append('<input class="btn btn-success editable" name="_save" value="✓ Save" onclick="savePerson()">');
    $tr.append('<input class="btn btn-warning editable" name="_cancel" value="✗ Cancel" onclick="editPerson()">');
    $tr.append('<input class="btn btn-danger display_only" name="_unlink" value="Remove attendee" onclick="unlinkPerson(8, 10)">');
    $tr.append('</td>');
    $('#attendees_table').append($tr);
    $('.editable').hide();
}


function getAttendees(url){
    $.get(url,  function (people_list){
    for (i = 0; i < people_list.length; i++){
        displayPerson(people_list[i]);
    }
    });
}

getAttendees('/api/events/8/participants');