// remove the delete button from the lower left side of pages
// This is SWOP's request, see https://github.com/OpenTechStrategies/swoptact/issues/52

function removeDefaultButtons() {
    // remove the delete button
    $("div.form-actions div.pull-left a.deletelink").remove();
    // remove the default "Done" button.  This was replaced by a new
    // button in templates/admin/inline_event_participants.html that
    // saves open rows and submits the form.
    $("div#form-actions div.pull-right input[name='_save'] ").remove();
    // add a "save and stay on page" button after the first fieldset
    $("div#form-actions div.pull-right ").appendTo("#fieldset-1");
    $("input[name='_continue']").attr("style", "display: block;");
    $("input[name='_continue']").attr("value", "Save Changes");
    $("input[name='_continue']").attr("class", "btn-primary btn default");
}

$(document).ready(function () {
    removeDefaultButtons();
});
