// remove the delete button from the lower left side of pages
// This is SWOP's request, see https://github.com/OpenTechStrategies/swoptact/issues/52

function removeDefaultButtons() {
    // Hide all right-hand inputs for a second
    $("#form-actions input").hide();
    // Make some changes to the "save and stay" button that we're interested in
    $("#form-actions input[name='_continue']").addClass("btn-primary btn default").val("Save Changes").show();

    // Move the right-hand button set to a position after the first fieldset.
    // We don't need it after ajax-generated table at the bottom of the form,
    // where saves are done immediately after editing within the table cell.
    $("#form-actions .pull-right").appendTo("#fieldset-1");
    
    // Remove the original "form-actions";
    $("#form-actions").remove();
}

$(document).ready(function () {
    removeDefaultButtons();
});
