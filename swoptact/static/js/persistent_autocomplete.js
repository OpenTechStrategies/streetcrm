function setupAutoCompleteCallbacks() {
    $.makeArray($(".persistent-autocomplete")).map(
        function (obj) {
            var jq_obj = $(obj);
            var options = $.parseJSON(jq_obj.attr("data-options"));
            var user_widget = jq_obj.find(".user-widget");

            user_widget.autocomplete({
                source: options,
            });
        });
}

$(document).ready(function () {
    setupAutoCompleteCallbacks();
});