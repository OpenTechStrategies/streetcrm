/*
Handle inline relationships, including many to many relationships,
in the Django admin via an ajax'y interface.

Some terminology:
 - the "page model" refers to the model primarily represented on this
   page
 - "inlined model" refers to any foreign model linked via this ajax'y
   form
*/

/* Gum-and-duct-tape string formatter

Arguments:
 - string_pattern: A "url pattern" which is a list of strings.
     Some of these will be "special", intended to be matched/replaced.
     By the end of this, all of these will be joined together,
     including the ones that are substitued.

Returns:
  A function which can be called with a single argument, an
  object/hashmap full of the components to be replaced.

Sounds confusing?  It's not too hard to use.  Take a look:
  var url_formatter = gummyStringFormatter(
                          ["/api/froobs/", "<froob_id>", "/lookit"]);
  // This should produce "/api/froobs/35/lookit"
  var my_url = url_formatter({"<froob_id>": 35});
*/

/* Prevent the enter key from submitting the form. Enter is now reserved
 * for submitting changes to individual entity values via the
 * click-to-edit UI. */

/* Since using "enter" to submit is one reason if not the main reason
 * for having <form> tags at all, one wonders if these might be done
 * away with entirely, with all network communication being done via
 * ajax instead */
$("form").keypress(function(e){
  if (e.which == 13) {
    return false;
  }
});

function gummyStringFormatter(string_pattern) {
    return function(replace_map) {
        var new_str = "";
        for (var i = 0; i < string_pattern.length; i++) {
            var component = string_pattern[i];
            if (component in replace_map) {
                new_str = new_str + replace_map[component];
            } else {
                new_str = new_str + component;
            }
        }
        return new_str;
    };
}


function setupStaticDiv(field_def, cur_value) {
    if (!cur_value) {
        cur_value = "";
    }
    var div_wrapper = $("<div class=\"static\"/>");
    div_wrapper.append("<span class=\"static-span\">" + cur_value + "</span>");
    return div_wrapper;
}

function setupEditableDiv(field_def, cur_value) {
    var div_wrapper = $("<div class=\"editable\"/>");
    var input = $("<input/>", {
        "class": "vTextField " + field_def["form_name"],
        "type": "text",
        "value": cur_value});
    input.text(cur_value);
    div_wrapper.append("<div class=\"validation-error\"/>");
    div_wrapper.append(input);
    return div_wrapper;
}

function getValueFromTextInput(column) {
    return column.find("input").val();
}

function setupAutoCompleteStaticDiv(field_def, cur_value) {
    if (cur_value) {
        return setupStaticDiv(field_def, cur_value.name);
    } else {
        return setupStaticDiv(field_def, "");
    }
}



/*
           ..   ..
            \.-./
      \     (o o)    \ 
      /\    /"""\    /\
           ''   ''
  BEWARE OF FALLING LAMBDAS!

... just kidding, everything's okay.  It's just a little bit more
intense of a function than I'd like.  Besides, every codebase needs
a reference to "lambda" to show the authors are with it, right?

Basically we're going to set up a field here for the autocomplete field.
But that thing needs to indicate clearly to the user when something
is new or not to the user, so we set up a [NEW] widget, hide it by default,
but as soon as a user types something, we check to see if that's new.

But we simultaneously also hook in the autocomplete stuff.  (Pull out
the URL for that out of the field definition!)  It turns out we've
already got an "on typing" handler there, so why not tack on the [NEW]
stuff when we run that?

So that's why this looks a bit tricky.  But it's not so bad.
*/

function setupAutoCompleteEditableDiv(field_def, cur_value) {
    // named_fkey has some more complex code...
    if (cur_value) {
        var named_fkey_div = setupEditableDiv(
            field_def, cur_value.name);
    } else {
        var named_fkey_div = setupEditableDiv(
            field_def, "");
    }

    var named_fkey_input = $(named_fkey_div.find("input")[0]);
    var new_indicator = $("<span class=\"new-indicator\">[NEW]</span>");
    named_fkey_div.append(new_indicator);
    new_indicator.hide();

    // Otherwise, check for whether or not this is a new item on each keydown
    // @@: Can we reduce a request per keystroke by rolling this into
    //   the autocomplete's signals?
    function maybeUpdateNew () {
        $.ajax({
            url: field_def.autocomplete_uri,
            datatype: "html",
            data: {
                q: named_fkey_input.val(),
            },
            success: function(data) {
                var lower_input = named_fkey_input.val().toLowerCase();
                var result_as_array = $.makeArray($(data));
                var found_match = false;
                // Search through all results, see if there's a match
                // that matches by lowercase
                for (var i = 0; i < result_as_array.length; i++) {
                    var this_result = result_as_array[i];
                    if ($(this_result).text().toLowerCase() == lower_input) {
                        found_match = true;
                        break;
                    }
                }

                // If there's a match, hide the [NEW], but show it otherwise
                if (found_match || lower_input.length == 0) {
                    new_indicator.hide();
                } else {
                    new_indicator.show();
                }
            }
        });
    }

    // Possibly update the [NEW] thing on keystroke
    named_fkey_div.on(
        "keyup",
        function (event) {
            // 13 is enter key, and we have a different handler for that
            if (event.which != 13) {
                maybeUpdateNew();
            }});

    // Named_fkey autocomplete stuff
    named_fkey_input.autocomplete({
        select: function (event, ui) {
            if (ui.item) {
                new_indicator.hide();
            }},
        source: autoCompleteSourceHelper(field_def.autocomplete_uri),
        // If we can focus on it, it's definitely not [NEW]
        focus: function (event, ui) {new_indicator.hide();},
        // But be sure after a close, we may have "reverted" the value
        close: function (event, ui) {maybeUpdateNew();},
    });

    return named_fkey_div;
}

var fieldTypes = {
    "text": {
        setupStatic: setupStaticDiv,
        setupEdit: setupEditableDiv,
        getValueFromColumn: getValueFromTextInput
    },
    "fkey_autocomplete_name": {
        setupStatic: setupAutoCompleteStaticDiv,
        setupEdit: setupAutoCompleteEditableDiv,
        getValueFromColumn: getValueFromTextInput
    }
};



function getRowValues(row) {
    var dict = {};
    $.makeArray(row.children("td[data-form-name]")).map(
        function(column) {
            var jq_column = $(column);
            var form_name = jq_column.attr("data-form-name");
            var input_type = jq_column.attr("data-input-type");
            var handler = fieldTypes[input_type].getValueFromColumn;
            dict[form_name] = handler(jq_column);
        }
    );
    return dict;
}

function rowIsEmpty(row) {
  var dict = getRowValues(row);
  // This is very simplistic for now. It seems very possible that we
  // might need more sophisticated ways of determining whether a row is
  // "empty" or not.
  for (prop in dict) {
    if (dict[prop] != "") return false;
  }
  return true;
}

/* Gets the model id this page represents. */
function getPageModelId() {
    return document.getElementById('page_model_object_id').value;
}

// TODO: We should memoize this on the object itself probably?
/* Grab the configuration for this whole inline ajax system

Said configuration is stored in a hidden input with the id
"inline-config" in a json-encoded "data-config" attribute
*/
function getInlineConfig() {
    return $.parseJSON($("#inline-config").attr("data-config"));
}

// Shortcut for getting the configuration
function getFieldsConfig() {
    return getInlineConfig()["fields"];
}

/* Isn't it rare and beautiful to use a switch statement with
 * intentional fall-through? Yes, yes it is.
 * This function associates a numerical value with each rank
 * so that ranks may be more easily compared to each other. */
function getUserRank(userGroup) {
    var rank = 0;
    switch (userGroup) {
      case "developer": rank++;
      case "admin": rank++;
      case "staff": rank++;
      case "leader": rank++;
    }
    return rank;
}

/* Check if the current user can edit the ajax tables based on user rank
 * and model. */
function userCanEdit() {
    var userRank = getUserRank(getInlineConfig()["user_group"]);
    var model = $("#model_name").val();
    switch (model) {
      case "event": return true;
      case "institution": return userRank > 2 ? true : false;
      default: return userRank > 3 ? true : false;
    }
}

// <inline_config_uri_helpers>
//   Various helpers for URI construction based on the inline form's
//   config, as supplied by the server

function getAutoCompleteUrl() {
    return getInlineConfig()["autocomplete_url"];
}

// @@: should these also be named get* rather than fill*?
function fillCurrentInlinesUrl(page_model_id) {
    var formatter = gummyStringFormatter(
        getInlineConfig()["current_inlines_for_page_url"]);
    return formatter({"<page_model_id>": page_model_id});
}

function fillLinkInlinedModelUrl(page_model_id, inlined_model_id) {
    var formatter = gummyStringFormatter(
        getInlineConfig()["link_inlined_model_url"]);
    return formatter({"<page_model_id>": page_model_id,
                      "<inlined_model_id>": inlined_model_id});
}

function fillExistingInlinedModelUrl(inlined_model_id) {
    var formatter = gummyStringFormatter(
        getInlineConfig()["existing_inlined_model_url"]);
    var formatter = formatter({"<inlined_model_id>": inlined_model_id});
    return formatter;
}

function getExistingInlinedModelProfileUrl(inlined_model_id, url_string) {
    if (url_string == undefined) { url_string=null; }
    var url_for_profile = "";
    if (url_string != null){
        url_for_profile = url_string + inlined_model_id;
    }
    else{
        var formatter = gummyStringFormatter(
            getInlineConfig()["existing_inlined_model_profile_url"]);
        url_for_profile = formatter({"<inlined_model_id>": inlined_model_id});
    }
    return url_for_profile;
}

function getNewInlinedModelUrl() {
    return getInlineConfig()["new_inlined_model_url"];
}

function getNewInlinedModelNamePlural() {
    return getInlineConfig()["inlined_model_name_plural"];
}

// </inline_config_uri_helpers>


function revertEditRow(inlined_model_id) {
    // TODO: base this on the filling system
}


/* Insert a inlined into the DOM.

Here, the inlined is a json object, as fetched from the API.
*/
function insertInlinedModel(inlined_model) {
    // TODO: Insert the inlined_model into a hashmap for later reference?
    //   (eg, if canceling an edit...)

    // Construct and insert table row
    // -------------------------------
    var tableRow = $("<tr />");
    tableRow.addClass("form-row");
    tableRow.data("id", inlined_model.id);

    fillTableRow(tableRow, inlined_model);

    // It's important that we append to the table before (possibly)
    // focusing on an input element below.
    $("#inlined-model-table").append(tableRow);

    // Special hacks for the "new" inlined_model...
    if (inlined_model.id === "") {
        var scrollableArea = $("#inlined-model-table").closest(".scrollable-area");
        // Turn on autocomplete,
        turnOnAttendeeAutocomplete(tableRow);
        // show the input field for the first field in the new model (and hide the static version),
        $(tableRow.find(".static")[0]).hide();
        $(tableRow.find(".editable")[0]).show();
        // scroll to the bottom of the table
        scrollableArea.scrollTop(scrollableArea.prop("scrollHeight"));
        // and put the focus on the input element.
        $(tableRow.find(".editable")[0]).find("input").focus();
    }
}


/* Helper utility for constructing autocomplete functions

Return a closure to help us construct autocomplete source functions
for things that use django_autocomplete_light with jquery ui's autocomplete

Arguments:
 - url: the URL used to construct
*/
function autoCompleteSourceHelper(url) {
    return function (request, response) {
        $.ajax({
            url: url,
            datatype: "html",
            data: {
                q: request.term
            },
            success: function(data) {
                var json_data = $.map(
                    $.makeArray($(data)),
                    function(elt) {
                        return {
                            "value": $(elt).text(),
                            "data": {"id": $(elt).attr("data-value")},
                            "label": $(elt).text()}});
                // massage data or in the select func?
                response(json_data);
            }});
    }
}


/* Turn on contact/attendee autocomplete.
 
Contact autocomplete is *only* on for completing the names of existing
inlined models when adding a new row!
*/
function turnOnAttendeeAutocomplete(edit_row) {

    // Hook in the autocomplete function
    edit_row.find("input.name").autocomplete({
        source: autoCompleteSourceHelper(getAutoCompleteUrl()),
        select: function(event, ui) {
            if (ui.item) {
                var inlined_model_id = ui.item.data.id;
                // Insert the inlined and make them immediately editable
                linkInlinedModel(inlined_model_id);
                // Don't replace the input value with the ui.item.value
                var tr =  $(this).closest("tr");
                // Hide the "new" row because removing it (below) causes a blur event in Chrome browsers (see the "blur" handler
                tr.hide();
                tr.remove();
                // Prevent form submission.
                event.preventDefault();
            }
        }
    });
}

/*
  Create a link to the change form of an inlined model with the given ID
*/
function createProfileLink(inlined_model_id, existing_element, url_for_profile) {
    if (url_for_profile == undefined) { url_for_profile = null; }
    var link_to_profile = $("<a/>");
    link_to_profile.html("<span class=\"large-info\">&#x2139;</span>");
    link_to_profile.attr("href", getExistingInlinedModelProfileUrl(inlined_model_id, url_for_profile));
    link_to_profile.attr("target", "_blank");
    existing_element.append(link_to_profile);
}


/* Fill the table row with the appropriate elements

Arguments:
 - row: jquery DOM element for this inlined <tr> row
 - inlined: mapping representing this linked model's data
*/
function fillTableRow(row, inlined_model) {
    var fields_config = getFieldsConfig();

    fields_config.map(
        function(field) {
            var staticDiv = fieldTypes[field.input_type].setupStatic(
                field,
                // The current representation for this field on the model
                inlined_model[field.form_name]);

            if (field['form_name'] == 'name'){
                createProfileLink(inlined_model.id, staticDiv);
            }
            else if (field['form_name'] == 'institution' && inlined_model.institution){
                // this doesn't work yet because I don't know how to set the URL correctly
                createProfileLink(inlined_model.institution.id, staticDiv, "/swoptact/institution/");
            }

            var editableDiv = fieldTypes[field.input_type].setupEdit(
                field,
                // The current representation for this field on the model
                inlined_model[field.form_name])

            td_wrap = $("<td/>");
            td_wrap.attr("data-form-name", field['form_name']);
            td_wrap.attr("data-input-type", field['input_type']);

            td_wrap.append(staticDiv);
            td_wrap.append(editableDiv);

            row.append(td_wrap);

        }
    );
    // Now append the buttons if the user has enough privileges
    // if (getInlineConfig()["user_can_edit"]) {
    //    row.append('<td><span class="deleteButton">&#10006;</span></td>');
    // }
    if (userCanEdit()) {
       row.append('<td><span class="deleteButton">&#10006;</span></td>');
    }
}


/*
  This works to show and hide a paticular message

  NB: You can only use showMessage for a single message
      calling it successively will cause the previous
      message to replaced with the new one.

  When calling this you should have the first parameter
  as the message text and the second parameter as the type
  of message it is:

  MESSAGE_SUCCESS (a green box)
  MESSAGE_INFO (a blue box)
  MESSAGE_WARNING (a yellow box)
  MESSAGE_ERROR (a red box)
*/

MESSAGE_SUCCESS = "alert-success";
MESSAGE_INFO = "alert-info";
MESSAGE_WARNING = "alert-warning";
MESSAGE_ERROR = "alert-danger";

/* Shows the message box */
function showMessage(error, message) {
    var errorBox = $("#inlined-error-box");
    // Firstly call the Message clean function this will ensure the
    // box is cleanly setup so we can display the message.
    cleanMessage();

    // Add the error class
    errorBox.addClass(error)

    // Add show the text
    errorBox.text(message);

    // ensure it's visable
    errorBox.css("visibility", "visible");
}

/* Hides the message box */
function hideMessage() {
    var errorBox = $("#inlined-error-box");

    // Clean it just in case.
    cleanMessage();

    // Hide the box
    errorBox.css("visibility", "hidden");
}

/* Cleans any extra things that has been added from the message box */
function cleanMessage() {
    var errorBox = $("#inlined-error-box");

    // firstly remove any extra classes on it.
    errorBox.removeClass();

    // Add back the base "alert" class
    errorBox.addClass("alert");

    // Remove any text inside
    errorBox.empty();
}

/* This shows limit reached message and disables the buttons to add more */
function limitReached(error, message) {
    // Populate default message if one isn't given
    if (!message) {
	var peopleLimit = getInlineConfig()["link_limit"];
	message = "You have reached the limit of " + peopleLimit + " contacts.";
    }

    // Show the error message
    showMessage(error, message);

    // Hide the "+ Add new" button
    var addNewButton = $("#add-new-inlined-model-btn");
    addNewButton.css("visibility", "hidden");
}

/* Checks if the limit has been reached - if so calls limitReached */
function checkLimitReached() {
    var peopleLimit = getInlineConfig()["link_limit"];

    // Check if there is a limit
    if (!peopleLimit) {
	return false;
    }

    // How many linked models do we have?
    var linkedModels = $("tr");

    // If it's less than the limit return false
    if (linkedModels.length < peopleLimit) {
	return false;

    }

    limitReached(MESSAGE_WARNING);
    return true;
}

/* Grab the initial list of linked items from the server & render */
function loadInitialAttendees() {
    var page_model_id = getPageModelId();
    var url = fillCurrentInlinesUrl(page_model_id);
    $.get(url, function (people_list) {
        for (i = 0; i < people_list.length; i++){
            insertInlinedModel(people_list[i]);
        }
        setStickyHeaders();
        // Check if we're over the limit and if so show a meesage
	// and stop the user adding more
	var peopleLimit = getInlineConfig()["link_limit"];
	if (peopleLimit && people_list.length >= peopleLimit) {
	    limitReached(MESSAGE_WARNING);
	}

    }, "json");
}


/* Add the inlined model on the backend and link on the frontend */
function linkInlinedModel(inlined_model_id) {
    var url = fillLinkInlinedModelUrl(getPageModelId(), inlined_model_id);
    $.post(url, function (result) {
        $.get(fillExistingInlinedModelUrl(inlined_model_id),
              function (inlined_model) {
                  insertInlinedModel(inlined_model);
              }, 'json');
    }, "json").fail(function (result) {
        error = JSON.parse(result.responseText)["error"];
        // Check for errors and if so display them.
        if (error) {
            limitReached(MESSAGE_ERROR, error);
        }
    });
}

/* Remove inlined model with INLINED_MODEL_ID from server and the UI. */
function unlinkInlinedModel(row){
    var inlined_model_id = row.data("id");
    var page_model_id = getPageModelId();
    var target_url = fillLinkInlinedModelUrl(page_model_id, inlined_model_id);
    $.ajax({
        url: target_url,
        type: 'DELETE',
        success: function() {row.fadeOut(800, function() { row.remove(); })}
    });
}


// @@: Shouldn't this be getting the failure descriptions from the server?
//     That would be more consistent with how django form errors are displayed
//     and would be much more flexible
//
// The displayed error messages are now coming from the server. To
// modify these, see formfields.py - NTT
function handleJSONErrors(errors, row){
    row.children("td").each(function() {
        var ths = $(this)
        var formName = ths.data("form-name");
        if (errors.hasOwnProperty(formName)) {
            var allErrors = errors[formName].join("; ");
            ths.find(".validation-error").text(allErrors);
            // Disable all sibling <td>s (except the delete row button)
            ths.addClass("corrigendum");
            ths.siblings("td:not(:has(span.deleteButton))").addClass("disabled");
        }
    });
}

/* Save inlined model on server and update the UI

Arguments:
 - inlined_model_id: the identifier for this linked model
 - submit_flag: whether or not to submit the entire form
   NOTE: this is broken, see issue #105
*/
function saveInlinedModel(row, cell) {
    var inlined_model_id = row.data("id");
    var form_data = getRowValues(row);

    // Handle if this is a new row, or an existing one
    //
    // @@: we shouldn't really have both "empty" and ""
    //   supported here.  We should simplify the code to just ""
    //   because otherwise we're going to end up with a lot of
    //   missed conditions and extra checks.
    if (inlined_model_id != "empty" && inlined_model_id != ""){
        return $.get(fillExistingInlinedModelUrl(inlined_model_id),
              function (inlined_model_dbstate) {
                  // @@: Unfortunately, we're fetching the existing representation from
                  //   the server and then modifying that with the form before update.
                  //   The reason is that whatever fields aren't supplied are dropped...
                  //   and we don't want that!
                  //   
                  //   ... this is potentially DANGEROUS depending on how the
                  //   page model is defined!  The API is non-symmetrical,
                  //   meaning that data representation of existing models is not
                  //   guaranteed (and often is not) the same as the representation
                  //   used to add new / save adjustments to models.
                  //   For example, a foreign key will return a hashmap of data
                  //   whereas a referenced-by-name-on-save will just take a string
                  //   back.  This means THIS WILL BREAK for this kind of data
                  //   if not represented in this field.
                  //
                  //   ... So if it's possible to only save adjustments to the fields
                  //   we're representing, we should do that. :P
                  //
                  // ... we're not doing a clean copy of this data, because it isn't
                  // necessary and it's not trivial to do in javascript, but keep
                  // in mind that this does mutate inlined_model_dbstate too.
                  //
                  var data_to_submit = inlined_model_dbstate;
                  for (key in form_data) {
                      data_to_submit[key] = form_data[key];
                  }
                  
                  $.ajax({
                      url: fillExistingInlinedModelUrl(inlined_model_id),
                      data: JSON.stringify(data_to_submit),
                      type: 'PUT',
                      error: function (response) {
                          var errors = jQuery.parseJSON(response.responseText).form.errors;
                          handleJSONErrors(errors, row);
                      },
                      success: function (response) {
                          checkLimitReached();
                          row.find("td").removeClass("disabled").removeClass("corrigendum");
                          cell.find(".validation-error").empty();
                          cell.find(".static").show();
                          cell.find(".editable").hide();
                      },
                      complete: function() {
                          // Reset sticky headers in case table cell widths have changed.
                          setStickyHeaders();
                      },
                      dataType: 'json'
                  });
              }, 'json');
    } else {
        return $.ajax({
            url: getNewInlinedModelUrl(),
            data: JSON.stringify(form_data),
            type: 'POST',
            error: function (response) {
                var errors = jQuery.parseJSON(response.responseText).form.errors;
                handleJSONErrors(errors, row);
            },
            success: function (response) {
                var url = fillLinkInlinedModelUrl(getPageModelId(), response.id);
                $.post(url, function (result) {
                    $.get(fillExistingInlinedModelUrl(response.id),
                          function (inlined_model) {
                              // remove the "new" row from the UI and add one by the same method others were added.
                              row.remove();
                              insertInlinedModel(inlined_model);
                              checkLimitReached();
                              // Not sure if the below are necessary since I don't think a row can qualify as
                              // "new" with a pre-existing error in one of the cells, but leaving in for now.
                              row.find("td").removeClass("disabled").removeClass("corrigendum");
                              cell.find(".validation-error").empty();
                              cell.find(".static").show();
                              cell.find(".editable").hide();
                          }, 'json');
                }, "json");
            },
            complete: function() {
                // Reset sticky headers in case table cell widths have changed.
                setStickyHeaders();
            },
            dataType: 'json'
        });
    }
}

function insertFieldsetHeader() {
    $("#js-fieldset-header").text(getNewInlinedModelNamePlural());
}

function insertFormHeaders() {
    getFieldsConfig().map(
        function(field) {
            var new_elt = $("<th/>");
            new_elt.text(field["descriptive_name"]);
            $("#inlined-model-table thead tr").append(new_elt);
        });
    if (userCanEdit()) {
        $("#inlined-model-table thead tr").append($("<th class=\"deleteButtonTH\">&nbsp;</th>"));
    }
}

function setStickyHeaders(e) {
    $("#inlined-model-table").stickyTableHeaders({
        scrollableArea: $(".scrollable-area")[0]
    });
}

/* Set up all the main widget callbacks */
function setupInlinedModelCallbacks() {
    // Adjust sticky headers on window resize
    $(window).on("resize", setStickyHeaders);

    if (userCanEdit()) {
        // Put the "add new" button into the form
        var addNewButton = $("<button type=\"submit\" class=\"btn-primary btn default\" name=\"_select\" id=\"add-new-inlined-model-btn\"></button>");
        // Get the button text from a Django function that translates according to user's locale.
        var addNewButtonText = "✚ " + gettext("Add New");
        addNewButton.text(addNewButtonText);

        addNewButton.on(
            "click",
            function(event) {
                event.preventDefault();
                insertInlinedModel({"id": ""});
            });

        $("#addNewButtonDiv").append(addNewButton);

        $("#inlined-model-table").on("keydown", "td .editable input", function(event) { console.log ("keydown: " + event.which); });
        $("#inlined-model-table").on(
            "keyup",
            "td .editable input",
            function (event) {
                if (event.which == 9 || event.which == 13) {  // "tab" and "enter", respectively
                    // Look for the next <td> that does not have a delete button
                    var next = $(this).closest("td").next("td:not(:has(span.deleteButton))");
                    if (next.length > 0) {
                        // The next cell is not the delete button. Only edit it if it's empty.
                        if (next.find("input").val().length == 0) {
                            next.trigger("click");
                        }
                    }
                    // else add a new row (but only if we're on the last row)
                    else if ($(this).closest("tr").next("tr").length == 0) {
                        $("#add-new-inlined-model-btn").trigger("click");
                    }
                    // This will trigger the blur handler (below) and submit the change
                    $(this).blur();
                }
            });

        // Add handler to make static divs in table turn magically into editable divs
        $("#inlined-model-table").on("click", "td", function(e) {
            if ($(this).hasClass("disabled")) {
                alert("This cell cannot be edited until errors in this row are corrected.");
            }
            else {                  
                $(this).children(".static").hide();
                $(this).children(".editable").show();
                var input = $(this).children(".editable").children("input");
                var len = input.val().length;
                input.focus();
                // Put cursor at end of input. Mult. len by 2 is a hack for Opera.
                input[0].setSelectionRange(len*2, len*2);
                // Reset sticky headers in case table cell widths have changed.
                setStickyHeaders();
            }
        });
        
        $("#inlined-model-table").on("blur", "td", function(e) {
            var row = $(this).closest("tr");
            var cell = $(this).closest("td");
            if (row.data("id") == "" && rowIsEmpty(row)) {
              // We've clicked out of a new and still empty row, so
              // leave without saving anything.
              row.remove();
              return false;
            }
            // Check whether the row containing this td is visible, and
            // only continue saving if is is. The row will not be
            // visible if this blur occurred when the user chose an
            // option from the autocomplete list of options.
            //
            // This check is needed for Chrom(e/ium) browsers.  In
            // Chrome, calling "remove" on the <tr> element (which
            // happens in the autocomplete "select" function) triggers
            // "blur".  In other browsers it doesn't, and we won't even
            // reach this point in the code, but for Chrome we hide the
            // row as a way of saying that autocomplete has taken over
            // and we don't need to save a new entity to the DB.
            if (row.is(":visible")) {
              // Update the UI with the new data.
              $(this).children(".static").children("span.static-span").text($(this).find("input").val());
              // Also save to the DB (arguably more important).
              saveInlinedModel(row, cell);
            }
        });
    
        // Handler on "delete row" buttons
        $("#inlined-model-table").on(
            "click", ".deleteButton",
            function() {
                unlinkInlinedModel($(this).closest("tr"));
            }
        );
    }
}

$(document).ready(function () {
    setupInlinedModelCallbacks();
    insertFormHeaders();
    insertFieldsetHeader();
    loadInitialAttendees();
});
