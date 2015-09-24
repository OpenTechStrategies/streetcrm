/* Set handler for form submit button. This hack became necessary when
 * the form tags in "change_form.html" were constricted in commit
 * 520bb44 to exclude the ajax-populated table in the lower section,
 * which is not part of the main form as the values in its fields are
 * saved immediately after entry and do not require a specific "submit"
 * action.  However, for aesthetic reasons, the submit button continues
 * to be placed at the bottom of the page, outside the form tags. Hence
 * we need this extra click handler. */
$(document).ready(function () {
    $("input[type=submit][name='_save']").on("click", function() { $("form.form-horizontal").submit(); });
});
