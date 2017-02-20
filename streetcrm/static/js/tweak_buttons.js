// Tweak "Save" buttons to get renamed to "Done"
function tweakSaveToDone() {
    $("input[type=\"submit\"][value=\"Save\"]").attr("value", "Done");
}

$(document).ready(tweakSaveToDone);
