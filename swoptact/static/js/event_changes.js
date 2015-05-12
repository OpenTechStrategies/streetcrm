/*
This page creates a jquery calendar for 
*/
function testFcn() {
    $('#id_is_prep').on(
        "click",
 	function(){
            $( ".row" ).eq(-1).toggle();
        });

    $(document).ready(function () {
        if ($('#id_is_prep').prop('checked')){
            $( ".row" ).eq(-1).show();
        }
        else{
            $( ".row" ).eq(-1).hide();
        }
    });


}

testFcn();