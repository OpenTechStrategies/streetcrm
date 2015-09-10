function setupAutoCompleteCallbacks() {
    $.makeArray($(".persistent-autocomplete")).map(
        function (obj) {
            var jq_obj = $(obj);
            var options = $.parseJSON(jq_obj.attr("data-options"));
            var option_names = Object.keys(options);
            jq_obj.find(".user-widget").autocomplete({
                source: option_names,
            });
        });
}

$(document).ready(function () {
    setupAutoCompleteCallbacks();
});