function textLimitCountdown() {
    // Find out the limit for the field
    var textLimit = $("#id_name").attr("size");
    var textElementName = $("#id_name").attr("name");

    // Check how many characters are left.
    var remainingChars = textLimit - $("#id_name").val().length;

    if (remainingChars <= 0) {
        $("#id_remaining").text("You have reached the character limit for the " + textElementName);
        $("#id_name_countdown_message").text("");
    } else {
        $("#id_remaining").html("&nbsp&nbsp&nbsp&nbsp characters remaining");
        $("#id_name_countdown_message").text(remainingChars);
    }
}

$(document).ready(function () {
    // Create the Text limit text box
    var spacingElement = $("<span></span>").attr("id", "id_name_spacing");
    var textLimitElement = $("<span></span>").attr("id", "id_name_countdown_message");
    var remainingElement = $("<span></span>").attr("id", "id_remaining");
    spacingElement.html("&nbsp");
    $("#id_name").after(spacingElement);
    spacingElement.after(textLimitElement);
    textLimitElement.after(remainingElement);
    // Call the text limit countdown to pre-fill the countdown for the first time
    textLimitCountdown();

    // Setup callbacks
    $("#id_name").keyup(textLimitCountdown);
});