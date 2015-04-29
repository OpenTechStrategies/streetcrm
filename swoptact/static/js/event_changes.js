/*
This page creates a jquery calendar for 
*/
function testFcn() {
    $('#id_is_prep').on(
        "click",
 	function(){
            $( ".row" ).last().toggle();
        });

    $(document).ready(function () {
 	$( ".row" ).last().hide();
    });


}

testFcn();