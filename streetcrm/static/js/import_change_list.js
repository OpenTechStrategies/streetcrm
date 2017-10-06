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
            },
            error: function (e) {
                toastMessage("There was an error with your import");
            }
        });
    });
}

$(document).ready( function () {
    setupChangelistFileImport();
});
