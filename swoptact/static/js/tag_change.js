function textLimitCountdown() {
    // Find out the limit for the field
    var textLimit = $("#id_name").attr("size");
    var textElementName = $("#id_name").attr("name");

    // Check how many characters are left.
    var remainingChars = textLimit - $("#id_name").val().length;

    if (remainingChars <= 0) {
        $("#id_name_countdown_message").text("You have reached the character limit for the " + textElementName);
    } else {
        $("#id_name_countdown_message").text(remainingChars + " characters remaining");
    }
}

$(document).ready(function () {
    // Create the Text limit text box
    var textLimitElement = $("<span></span>").attr("id", "id_name_countdown_message");
    $("#id_name").after(textLimitElement);

    // Call the text limit countdown to pre-fill the countdown for the first time
    textLimitCountdown();

    // Setup callbacks
    $("#id_name").keyup(textLimitCountdown);
});