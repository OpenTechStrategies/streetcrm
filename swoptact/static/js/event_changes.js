/*
This page creates a jquery calendar for 
*/
function toggleMajorActionRow(){
    if ($('#id_is_prep').prop('checked')){
        $( ".row" ).eq(-1).show();
    }
    else{
        $( ".row" ).eq(-1).hide();
    }
}

function loadMajorAction() {
    $('#id_is_prep').on(
        "click",
 	function(){
            toggleMajorActionRow();
        });

    $(document).ready(function () {
        toggleMajorActionRow();
    });


}

loadMajorAction();
