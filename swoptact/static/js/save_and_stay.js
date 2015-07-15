function addSaveAndStayButton() {
    // add a "save and stay on page" button after the first fieldset
    $("input[name='_continue'] ").appendTo("#fieldset-1");
    $("input[name='_continue']").attr("style", "display: block; float: right;");
    $("input[name='_continue']").attr("value", "Save Changes");
    $("input[name='_continue']").attr("class", "btn-primary btn default");
}

$(document).ready(function () {
    addSaveAndStayButton();
});
