/*
This page creates a jquery calendar for 
*/
function testFcn() {
    $('#id_is_prep').on(
        "click",
 	function(){
            $( ".row" ).eq(-2).toggle();
        });

    $(document).ready(function () {
        if ($('#id_is_prep').prop('checked')){
            console.log($( ".row" ).eq(-2).value);
            $( ".row" ).eq(-2).show();
        }
        else{
            $( ".row" ).eq(-2).hide();
        }
    });


}

testFcn();