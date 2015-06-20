// remove the delete button from the lower left side of pages
// This is SWOP's request, see https://github.com/OpenTechStrategies/swoptact/issues/52

function removeDefaultButtons() {
    $("div.form-actions div.pull-left a.deletelink").remove();
    $("div#form-actions div.pull-right ").remove();
}

$(document).ready(function () {
    removeDefaultButtons();
});
