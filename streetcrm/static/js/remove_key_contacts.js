/*
 * This page manages the "Remove" buttons in the Key Contacts inline of
 * the Institutions change form.
 *
*/

/*
 * Stole this function from "inline_ajax.js" Doubtless we should keep
 * shared functions like this in some other file.
 *
*/
function getParticipantIdForRow(jq_element) {
    // Take a jquery element for any member of a participant row
    // and extract the participant id (returned as a string)
    return jq_element.parents("tr").children(".participant-id")[0].value;
}

/*
 * Get the id of the institution the user is currently viewing/editing.
 *
*/
function getInstitutionId(){
    return document.getElementById('institution_object_id').value;
}

/*
 * Remove contact from the institution (but not the participant from the
 * database).
 *
*/
function unlinkContact(participant_id){
    var institution_id = getInstitutionId();
    var target_url = '/api/institutions/'+institution_id+'/participants/'+participant_id+'/';
    $.ajax({
        url: target_url,
        type: 'DELETE',
        success: function (response) {
            console.log(response); 
        },
        error: function (response) {
            console.log(response);
        }
    });

}


/*
 * After the contact has been removed from the institution, immediately
 * hide the row from the user so the success of the removal is clear.
 *
*/
function hideRemovedRow(participant_id) {
    //get the hidden element with this value
    jq_element = $(".participant-id[value="+participant_id+"]");
    //get the row of that element
    var row = jq_element.parents("tr");
    //hide the row
    row.hide();
}

function setUpContactCallbacks() {

    $(document).ready(function () {
        $("#contacts-table").on(
            "click", "button.contact-unlink",
            function(event) {
                event.preventDefault();
                unlinkContact(getParticipantIdForRow($(this)));
                hideRemovedRow(getParticipantIdForRow($(this)));
            });

    });

}

setUpContactCallbacks();