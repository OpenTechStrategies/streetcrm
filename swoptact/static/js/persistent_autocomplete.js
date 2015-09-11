function setupAutoCompleteCallbacks() {
    $.makeArray($(".persistent-autocomplete")).map(
        function (obj) {
            var jq_obj = $(obj);
            var options = $.parseJSON(jq_obj.attr("data-options"));
            var option_names = Object.keys(options);
            var user_widget = jq_obj.find(".user-widget");
            var real_val_widget = jq_obj.find(".real-value");

            function maybeUpdateHiddenValue() {
                var selected_val = options[user_widget.val()];
                if (selected_val) {
                    real_val_widget.val(selected_val);
                }
            }
            

            function updateCallback(event, ui) {
                maybeUpdateHiddenValue();
            }

            user_widget.autocomplete({
                source: option_names,
                select: updateCallback,
                focus: updateCallback,
                close: updateCallback,
            });

            // Update on keystroke too
            user_widget.on(
                "keyup",
                function (event) {
                    // 13 is enter key, and we have a different handler for that
                    if (event.which != 13) {
                        maybeUpdateHiddenValue();
                    }});
        });
}

$(document).ready(function () {
    setupAutoCompleteCallbacks();
});