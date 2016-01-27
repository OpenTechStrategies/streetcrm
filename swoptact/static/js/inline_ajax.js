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


/* Generate a new <tr> element including all internal structures and
 * handlers, but no data. */
function getNewTableRow() {
    var tableRow = $("<tr />");
    tableRow.addClass("form-row");

    var fields_config = getFieldsConfig();

    fields_config.map(function(field) {
        var staticDiv = $("<div class=\"static\"/>");
        staticDiv.append("<span class=\"static-span\"/>");
        staticDiv.append("<a class=\"profile-link\" target=\"_blank\"><span class=\"large-info\">&#x2139;</span>");

        var editableDiv = $("<div class=\"editable\"/>");
        editableDiv.append("<div class=\"validation-error\"/>");

        var input = $("<input class=\"vTextField " + field["form_name"] + "\" type=\"text\"/>");
        editableDiv.append(input);
        
        if (field["input_type"] == "fkey_autocomplete_name") {
            var newIndicator = $("<span class=\"new-indicator\">[NEW]</span>");
            newIndicator.hide();
            editableDiv.append(newIndicator);

            // Possibly update the [NEW] label on keystroke
            input.on("keyup", function (e) {
                // 13 is enter key, and we have a different handler for that
                if (e.which != 13) {
                    maybeUpdateNew(newIndicator, input.val(), field["autocomplete_uri"]);
                }
            });

            // Named_fkey autocomplete stuff
            input.autocomplete({
                select: function (e, ui) {
                    if (ui.item) {
                        newIndicator.hide();
                    }
                },
                source: autoCompleteSourceHelper(field["autocomplete_uri"]),
                // If we can focus on it, it's definitely not [NEW]
                focus: function (event, ui) {newIndicator.hide();},
                // But be sure after a close, we may have "reverted" the value
                close: function (event, ui) {maybeUpdateNew(newIndicator, input.val(), field["autocomplete_uri"]);}
            });
        }

        var td_wrap = $("<td/ id=\"col-" + tableRow.children("td").length + "\">");
        td_wrap.attr("data-form-name", field["form_name"]);
        td_wrap.attr("data-input-type", field["input_type"]);

        td_wrap.append(staticDiv);
        td_wrap.append(editableDiv);

        tableRow.append(td_wrap);
    });

    // Now append the delete button if the user has enough privileges
    if (userCanDelete()) {
       tableRow.append('<td><span class="deleteButton">&#10006;</span></td>');
    }

    return tableRow;
}

function getValueFromTextInput(column) {
    return column.find("input").val();
}

// Check for whether or not this is a new item on each keydown
function maybeUpdateNew (newIndicator, val, autocomplete_uri) {
    $.ajax({
        url: autocomplete_uri,
        datatype: "html",
        data: {
            q: val,
        },
        success: function(data) {
            var lower_input = val.toLowerCase();
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
                newIndicator.hide();
            } else {
                newIndicator.show();
            }
        }
    });
}

function getRowValues(row) {
    var dict = {};
    $.makeArray(row.children("td[data-form-name]")).map(
        function(column) {
            var jq_column = $(column);
            var form_name = jq_column.attr("data-form-name");
            var input_type = jq_column.attr("data-input-type");
            dict[form_name] = getValueFromTextInput(jq_column);
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

/* Check if the current user can delete a user row from an ajax table,
   based on user rank and model. */
function userCanDelete() {
    var userRank = getUserRank(getInlineConfig()["user_group"]);
    var model = $("#model_name").val();
    switch (model) {
      case "event":
      case "institution": 
        return userRank > 2 ? true : false;
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
function turnOnAttendeeAutocomplete(tableRow) {
    // Hook in the autocomplete function
    tableRow.find("input.name").autocomplete({
        source: autoCompleteSourceHelper(getAutoCompleteUrl()),
        select: function(event, ui) {
            if (ui.item) {
                var inlined_model_id = ui.item.data.id;
                // Insert the inlined and make them immediately editable
                linkInlinedModel(tableRow, inlined_model_id);
            }
            // We must stop event propagation so that if the user
            // selected an autocomplete option by hitting 'enter', that
            // keydown event will not be interpreted as "save and move
            // the the next cell for further data entry".
            event.stopPropagation();
        }
    });
}

/*
  Create a link to the change form of an inlined model with the given ID
*/
function createProfileLink(model, cell) {
    var id, url;
    if (cell.data("form-name") == "name") {
        id = model.id;
        url = null;
    }
    else if (cell.data("form-name") == "institution" && model.institution) {
        id = model.institution.id;
        url = "/swoptact/institution/";
    }
    if (id != undefined) {
        // Give the profile link an href attribute and make it visible.
        var profileLink = cell.children(".static").children("a.profile-link");
        profileLink.attr("href", getExistingInlinedModelProfileUrl(id, url));
        profileLink.css("visibility", "visible");
    }
}


/* Populate the table row with values

Arguments:
 - row: a <tr> element with all structure but no data
 - inlinedModel: mapping representing this linked model's data
*/
function fillTableRow(tableRow) {
    var inlinedModel = tableRow.data("model");
    var staticDiv, editableDiv, fieldName, val;
    tableRow.children("td").each(function() {
        var cell = $(this);
        staticDiv = cell.children(".static");
        editableDiv = cell.children(".editable");
        fieldName = cell.data("form-name");
        if (cell.data("input-type") == "fkey_autocomplete_name") {
            val = inlinedModel[fieldName] ? inlinedModel[fieldName].name : "";
        }
        else {
            val = inlinedModel[fieldName] ? inlinedModel[fieldName] : "";
        }           
        staticDiv.children(".static-span").text(val);
        editableDiv.children("input").val(val);
        // Add a profile link (letter "i" in a circle)
        createProfileLink(inlinedModel, cell);
    });
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
function showMessage(level, message) {
    var errorBox = $("#inlined-error-box");
    // Firstly call the Message clean function this will ensure the
    // box is cleanly setup so we can display the message.
    // firstly remove any extra classes on it.
    errorBox.removeClass();

    // Add back the base "alert" class
    errorBox.addClass("alert");

    // Remove any text inside
    errorBox.empty();

    // Add stylings for success, error, etc.
    errorBox.addClass(level)

    // Add show the text
    errorBox.text(message);

    // ensure it's visable
    errorBox.show();
}

/* Hides the message box */
function hideMessage() {
    $("#inlined-error-box").hide();
}

/* This shows limit reached message and disables the buttons to add more */
function limitReached(message) {
    // Populate default message if one isn't given
    if (!message) {
        var peopleLimit = getInlineConfig()["link_limit"];
        message = "You have reached the limit of " + peopleLimit + " contacts.";
    }

    // Show the error message
    showMessage(MESSAGE_WARNING, message);
}

/* Checks if the limit has been reached - if so calls limitReached */
function checkLimitReached() {
    var peopleLimit = getInlineConfig()["link_limit"];

    // Check if there is a limit
    if (peopleLimit && $("#inlined-model-table tbody tr").length >= peopleLimit) {
        return true;
    }
    else {
        return false;
    }
}

/* Grab the initial list of linked items from the server & render */
function loadInitialAttendees() {
    var page_model_id = getPageModelId();
    var url = fillCurrentInlinesUrl(page_model_id);
    $.get(url, function (people_list) {
        var newRow;
        for (i = 0; i < people_list.length; i++){
            newRow = getNewTableRow();
            newRow.data("model", people_list[i]);
            fillTableRow(newRow);
            $("#inlined-model-table").append(newRow);
        }
        setStickyHeaders();
        // Warn the user if we're at the max number of contacts.
        if (checkLimitReached() == true) {
            limitReached();
        }
    }, "json");
}


/* Add the inlined model on the backend and link on the frontend */
function linkInlinedModel(tableRow, inlined_model_id) {
    var url = fillLinkInlinedModelUrl(getPageModelId(), inlined_model_id);
    $.post(url, function (result) {
        $.get(fillExistingInlinedModelUrl(inlined_model_id),
            function (existing_model) {
                tableRow.data("model", existing_model);
                fillTableRow(tableRow);
                // User just filled table row by selecting an autocomplete
                // option. Open a new row if it was the last row.
                if (tableRow.next("tr").length == 0) {
                    $("#add-new-inlined-model-btn").trigger("click");
                }
                // else close the cell we're working on by triggering a click event
                // that will close any cells being edited and save the new values.
                else {
                    // It won't close an element with the focus though, so blur it.
                    $(document.activeElement).blur();
                    $(document).trigger("click");
                }
            },
        "json");
    }, "json").fail(function (result) {
        message = JSON.parse(result.responseText)["error"];
        // Check for errors and if so display them.
        if (error) {
            showMessage(MESSAGE_ERROR, message);
        }
    });
}

/* Remove inlined model with INLINED_MODEL_ID from server and the UI. */
function unlinkInlinedModel(row){
    var inlined_model_id = row.data("model").id;
    var page_model_id = getPageModelId();
    var target_url = fillLinkInlinedModelUrl(page_model_id, inlined_model_id);
    $.ajax({
        url: target_url,
        type: 'DELETE',
        success: function() {row.fadeOut(800, function() { row.remove(); if (checkLimitReached() == false) { hideMessage(); } })}
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
            // Adding the error message into the cell may change the
            // cell's dimensions, which may change the dimensions of
            // other cells, which may move the relevant cell out of the
            // constant-height viewport that is part of the sticky table
            // headers implementation. Therefore make sure the distance
            // between the top of the errored cell and the top of the
            // viewport remains constant.

            // Measure position before the text is added...
            var pos1 = $(this).position().top;
            $(this).find(".validation-error").text(allErrors);
            // and after.
            var pos2 = $(this).position().top;

            // Then scroll into position. Note that the value of
            // scrollableArea.scrollTop() after adding the text
            // will be the same as it was before.
            var scrollableArea = $("#inlined-model-table").closest(".scrollable-area");            
            scrollableArea.scrollTop(scrollableArea.scrollTop() + (pos2-pos1));
            
            // If the error is on the bottom row, the bottom of the cell
            // might still be out of view. If this is the case, scroll a
            // little more (and add 15 px for padding).
            var offsetDifference = ($(this).offset().top + $(this).outerHeight() + 15) - (scrollableArea.offset().top + scrollableArea.outerHeight());
            if (offsetDifference > 0) {
                scrollableArea.scrollTop(scrollableArea.scrollTop() + offsetDifference);
            }

            // Mark the errored cell as such.
            ths.addClass("corrigendum");
            // Disable all sibling <td>s (except the delete row button)
            ths.siblings("td:not(:has(span.deleteButton))").addClass("disabled");            
        }
    });
}

/* Save inlined model on server and update the UI

Arguments:
 - inlined_model: this linked model
 - submit_flag: whether or not to submit the entire form
   NOTE: this is broken, see issue #105
*/
function saveInlinedModel(row, cell) {
    var inlined_model = row.data("model");
    var form_data = getRowValues(row);

    // Handle if this is a new row, or an existing one
    //
    // @@: we shouldn't really have both "empty" and ""
    //   supported here.  We should simplify the code to just ""
    //   because otherwise we're going to end up with a lot of
    //   missed conditions and extra checks.
    if (inlined_model.id != "empty" && inlined_model.id != ""){
        return $.get(fillExistingInlinedModelUrl(inlined_model.id),
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
                      url: fillExistingInlinedModelUrl(inlined_model.id),
                      data: JSON.stringify(data_to_submit),
                      type: 'PUT',
                      error: function (response) {
                          var errors = jQuery.parseJSON(response.responseText).form.errors;
                          handleJSONErrors(errors, row);
                      },
                      success: function (updated_model) {
                          if (checkLimitReached() == true) { limitReached(); }
                          row.find("td").removeClass("disabled").removeClass("corrigendum");
                          cell.find(".validation-error").empty();
                          cell.children(".static").children("span.static-span").text(cell.find("input").val());
                          createProfileLink(updated_model, cell);
                          row.data("model", updated_model);
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
                          function (updated_model) {
                              row.data("model", updated_model);
                              fillTableRow(row);
                              if (checkLimitReached() == true) { limitReached(); }
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
    if (userCanDelete()) {
        $("#inlined-model-table thead tr").append($("<th class=\"deleteButtonTH\">&nbsp;</th>"));
    }
}

function setStickyHeaders(e) {
    $("#inlined-model-table").stickyTableHeaders({
        scrollableArea: $(".scrollable-area")[0]
    });
}

function turnOnEditing(cell) {
    cell.children(".static").hide();
    cell.children(".editable").show();
    var input = cell.children(".editable").children("input");
    var val = input.val();
    input.focus();
    if (val) {
        // Put cursor at end of input. Mult. len by 2 is a hack for Opera.
        input[0].setSelectionRange(val.length*2, val.length*2);
    }
    // Reset sticky headers in case table cell widths have changed.
    setStickyHeaders();
}

/* Set up all the main widget callbacks */
function setupInlinedModelCallbacks() {
    // Adjust sticky headers on window resize
    $(window).on("resize", setStickyHeaders);


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

    if (userCanEdit()) {
        // Put the "add new" button into the form
        var addNewButton = $("<button type=\"submit\" class=\"btn-primary btn default\" name=\"_select\" id=\"add-new-inlined-model-btn\"></button>");
        // Get the name of the page model (Institution or Action) and
        // then set the name of the inlined model
        var page_model_name = $("#page_model_name").val();
        var inlined_model_name = "";
        if (page_model_name == "institution") {
            inlined_model_name = "contact";
        }
        else if (page_model_name == "event") {
            inlined_model_name = "attendee";
        }
        // Get the button text from a Django function that translates according to user's locale.
        var addNewButtonText = "✚ " + gettext("Add new") + " " + inlined_model_name;
        addNewButton.text(addNewButtonText);

        addNewButton.on("click", function(event) {
            // event.preventDefault(); commenting this out until I understand what it does.
            if (!checkLimitReached()) {
                var newRow = getNewTableRow();
                newRow.data("model", {"id": ""});  // This seems hacky. Find a better way.
                fillTableRow(newRow);
                $("#inlined-model-table").append(newRow);

                // Turn on autocomplete for attendee names (only applies to new rows).
                turnOnAttendeeAutocomplete(newRow);
                // scroll to the bottom of the table
                var scrollableArea = $("#inlined-model-table").closest(".scrollable-area");
                scrollableArea.scrollTop(scrollableArea.prop("scrollHeight"));
                turnOnEditing(newRow.children("td:first-of-type"));
            }
            else {
                var inlinedErrorBox = $("#inlined-error-box");
                if (inlinedErrorBox.is(":visible")) {
                    // This requires the animate-colors library for jQuery
                    var origBackground = inlinedErrorBox.css("background-color");
                    inlinedErrorBox.css("background-color", "red");
                    inlinedErrorBox.animate({"backgroundColor": origBackground}, 1000);
                }
                else {
                    limitReached();
                }
            }
        });

        $("#addNewButtonDiv").append(addNewButton);

        /* On any click in the document, check to see if we need to save any
           data in the ajax-populated table. */
        $(document).on("click", function(e) {
            // Find the closest editable div to the clicked element.
            var closest = $(document.activeElement).closest("td");

            // Loop through all visible editable divs and save their data;
            // but if the click occured in an editable div, skip that one.
            $("#inlined-model-table td:has(.editable:visible)").not(closest).each(function() {
                var row = $(this).closest("tr");
                var cell = $(this);  // a td object
                if (row.data("model").id == "" && rowIsEmpty(row)) {
                    // We've clicked out of a new and still empty row, so
                    // leave without saving anything.
                    row.remove();
                }
                else {
                    // Update the UI with the new data.
                    saveInlinedModel(row, cell);
                }
            });
        });

        $("#inlined-model-table").on(
            "keydown",
            "td .editable input",
            function (event) {
                if (event.which == 9 || event.which == 13) {  // "tab" and "enter", respectively
                    // Look for the next <td> that does not have a delete button
                    var next = $(this).closest("td").next("td:not(:has(span.deleteButton))");
                    if (next.length > 0) {
                        // The next cell is not the delete button. Only edit it if it's empty.
                        if (next.find("input").val().length == 0) {
                            // This will trigger other editable divs to be saved and closed.
                            next.trigger("click");
                        }
                    }
                    // else add a new row (but only if we're on the last row)
                    else if ($(this).closest("tr").next("tr").length == 0) {
                        $("#add-new-inlined-model-btn").trigger("click");
                    }
                    // else close the cell we're working on by triggering a click event
                    // that will close any cells being edited and save the new values.
                    else {
                        // It won't close an element with the focus though, so blur it.
                        $(document.activeElement).blur();
                        $(document).trigger("click");
                    }
                    event.stopPropagation();
                    return false; // This is also necessary to prevent default TAB action.
                }
            });

        // Add handler to make static divs in table turn magically into editable divs
        $("#inlined-model-table").on("click", "td", function(e) {
            if ($(e.target).hasClass("large-info")) {
                // The user clicked on a profile link, so don't do anything.
                return;
            }
            // else
            if ($(this).hasClass("disabled")) {
                alert("This cell cannot be edited until errors in this row are corrected.");
            }
            else {
                turnOnEditing($(this));
            }
            // The click event will now bubble up to the document level,
            // where any other cells being edited will be saved and
            // closed.
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
