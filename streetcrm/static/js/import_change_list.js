/*
 * Initializes the import button on change list pages
 *
*/

function setupChangelistFileImport() {
    $("#file-input").on("change", function (event) {
        var form = new FormData();
        form.append("file", event.target.files[0]);
        $.ajax({
            url: $("#file-input").data("path"),
            type: "POST",
            processData: false,
            contentType: false,
            data: form,
            success: function (data) {
                toastMessage(data.created_objects.length + " records created");
                setTimeout(function() { window.location.href = window.location.href; }, 2500);
            },
            error: function (e) {
                toastMessage("There was an error with your import. See more information on imports " +
                             "on <a href='/help'>the help page.</a>");
            }
        });
    });
}

$(document).ready( function () {
    setupChangelistFileImport();
});
