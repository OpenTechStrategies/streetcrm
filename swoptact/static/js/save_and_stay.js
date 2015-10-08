function addSaveAndStayButton() {
    // add a "save and stay on page" button after the first fieldset
    $("input[name='_continue'] ").appendTo("#fieldset-1");
    $("input[name='_continue']").attr("style", "display: block; float: right;");
    $("input[name='_continue']").attr("value", "Save Changes");
    $("input[name='_continue']").attr("class", "btn-primary btn default");
}

function addInstitutionLink() {
    var institutionID = $("#Institution-hidden-value").val();
    if (institutionID != "None") {
        // get the div that holds the institution:
        var staticDiv = $("input[name=institution]").parent();
        // add a link to it
        staticDiv.append("<a class=\"profile-link\" id=\"institution-link\" target=\"_blank\"><span class=\"large-info\">&#x2139;</span>");
        var profileLink = $("#institution-link");
        profileLink.attr("href", "/swoptact/institution/" + institutionID + "/");
    }
}

function toggleExtraActions() {
    $("tr.more_actions").hide();
    $("#toggle_more_actions").on("click", function () {
        $("tr.more_actions").toggle();
    });
}

$(document).ready( function () {
    addSaveAndStayButton();
    addInstitutionLink();
    toggleExtraActions();
});
