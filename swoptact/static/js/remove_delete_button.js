// remove the delete button from the lower left side of pages
// This is SWOP's request, see https://github.com/OpenTechStrategies/swoptact/issues/52
function removeDeleteButton() {
    $("div.form-actions div.pull-left a.deletelink").remove();
}

$(document).ready(removeDeleteButton);
