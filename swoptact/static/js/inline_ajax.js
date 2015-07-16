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


function setupTextInputStatic(field_def, cur_value) {
    if (!cur_value) {
        cur_value = "";
    }
    var p_elt = $("<p/>",
        {"style": "font-size: 18"});
    p_elt.text(cur_value);
    return p_elt
}

function setupTextInputEditable(field_def, cur_value) {
    input_elt = $("<input/>", {
        "class": "vTextField " + field_def["form_name"],
        "type": "text",
        "value": cur_value});
    input_elt.text(cur_value);
    return input_elt;
}

function getDataFromTextInput(column) {
    return column.find("input").val();
}

function setupFkeyAutoCompleteNameStatic(field_def, cur_value) {
    if (cur_value) {
        return setupTextInputStatic(field_def, cur_value.name);
    } else {
        return setupTextInputStatic(field_def, "");
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

function setupFkeyAutoCompleteNameEditable(field_def, cur_value) {
    div_wrapper = $("<div/>");
    // named_fkey has some more complex code...
    if (cur_value) {
        var named_fkey_input = setupTextInputEditable(
            field_def, cur_value.name);
    } else {
        var named_fkey_input = setupTextInputEditable(
            field_def, "");
    }
    div_wrapper.append(named_fkey_input);

    var new_indicator = $("<span class=\"new-indicator\">[NEW]</span>");
    div_wrapper.append(new_indicator);
    new_indicator.hide();

    // Named_fkey autocomplete stuff
    named_fkey_input.autocomplete({
        select: function (event, ui) {
            if (ui.item) {
                new_indicator.hide();
            }},
        source: autoCompleteSourceHelper(field_def.autocomplete_uri)});

    // Otherwise, check for whether or not this is a new item on each keydown
    // @@: Can we reduce a request per keystroke by rolling this into
    //   the autocomplete's signals?
    named_fkey_input.on(
        "keypress",
        function (event) {
            // 13 is enter key, and we have a different handler for that
            if (event.which != 13) {
                // Do we have an item that matches this?
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
                })
            }
        });

    return div_wrapper;
}

var fieldTypes = {
    "text": {
        setupStatic: setupTextInputStatic,
        setupEdit: setupTextInputEditable,
        getDataFromColumn: getDataFromTextInput
    },
    "fkey_autocomplete_name": {
        setupStatic: setupFkeyAutoCompleteNameStatic,
        setupEdit: setupFkeyAutoCompleteNameEditable,
        getDataFromColumn: getDataFromTextInput
    }
};



function getDataForEditRow(row) {
    var data = {};
    $.makeArray(row.children("td[data-form-name]")).map(
        function(column) {
            var jq_column = $(column);
            var form_name = jq_column.attr("data-form-name");
            var input_type = jq_column.attr("data-input-type");
            var handler = fieldTypes[input_type].getDataFromColumn;
            data[form_name] = handler(jq_column);
        }
    );
    return data;
}


// Hide and show stuff

function getInlinedModelStaticRow(inlined_model_id) {
    return $("#inlined-model-static-" + inlined_model_id);
}
function hideInlinedModelStaticRow(inlined_model_id) {
    getInlinedModelStaticRow(inlined_model_id).hide();
}
function showInlinedModelStaticRow(inlined_model_id) {
    getInlinedModelStaticRow(inlined_model_id).show();
}


function getInlinedModelEditRow(inlined_model_id) {
    return $("#inlined-model-edit-" + inlined_model_id);
}
function hideInlinedModelEditRow(inlined_model_id) {
    getInlinedModelEditRow(inlined_model_id).hide();
}
function showInlinedModelEditRow(inlined_model_id) {
    getInlinedModelEditRow(inlined_model_id).show();
}


function getInlinedModelErrorsRow(inlined_model_id) {
    return $("#inlined-model-errors-" + inlined_model_id);
}
function hideInlinedModelErrorsRow(inlined_model_id) {
    getInlinedModelErrorsRow(inlined_model_id).hide();
}
function showInlinedModelErrorsRow(inlined_model_id) {
    getInlinedModelErrorsRow(inlined_model_id).show();
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
    return formatter({"<inlined_model_id>": inlined_model_id});
}

function getExistingInlinedModelProfileUrl(inlined_model_id, url_string=null) {
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


/* Handle the "edit" button for a inlined row. */
function makeInlinedModelEditable(inlined_model_id) {
    // TODO: Copy data into the edit form

    // Hide display-only form
    hideInlinedModelStaticRow(inlined_model_id);
    // Show edit form
    showInlinedModelEditRow(inlined_model_id);
}

/* Handle the "cancel" button for a inlined edit-in-progress. */
function cancelInlinedModelEdit(inlined_model_id) {
    // Oh, this is the add new one... well, we don't need to switch
    // back to a static view.  Just dump it.
    if (inlined_model_id == "") {
        unlinkInlinedModel(inlined_model_id);
    }

    // TODO: Do a *real* revert of the data here!
    //// Revert and hide edit form
    // revertEditRow(inlined_model_id);
    hideInlinedModelEditRow(inlined_model_id);

    // Hide and clear errors form
    hideInlinedModelErrorsRow(inlined_model_id);
    clearErrors(inlined_model_id);

    // Show display-only form
    showInlinedModelStaticRow(inlined_model_id);
}


function revertEditRow(inlined_model_id) {
    // TODO: base this on the filling system
}


/* Wipe the errors row by filling it with nothing */
function clearErrors(inlined_model_id) {
    fillErrorsRow(getInlinedModelErrorsRow(inlined_model_id), inlined_model_id, []);
}


/* Take the current DOM element, find the parent row, and fetch the
   inlined model's id from it */
function getInlinedModelIdForRow(jq_element) {
    // Take a jquery element for any member of a inlined row
    // and extract the inlined id (returned as a string)
    return jq_element.parents("tr").children(".inlined-model-id")[0].value;
}


/* Insert a inlined into the DOM.

Here, the inlined is a json object, as fetched from the API.
*/
function insertInlinedModel(inlined_model) {
    // TODO: Insert the inlined_model into a hashmap for later reference?
    //   (eg, if canceling an edit...)

    // Construct and insert static row
    // -------------------------------
    var static_row = $(
        "<tr />",
        {"class": "form-row inlined-model-static",
         "id": "inlined-model-static-" + inlined_model.id});
    fillStaticRow(static_row, inlined_model);
    $("#inlined-model-table tbody").append(static_row);
    // Construct and insert error row (empty for now)
    // ----------------------------------------------
    var errors_row = $(
        "<tr />",
        {"class": "form-row inlined-model-errors",
         "id": "inlined-model-errors-" + inlined_model.id});
    errors_row.hide()
    fillErrorsRow(errors_row, inlined_model.id, []);
    $("#inlined-model-table tbody").append(errors_row);

    // Construct and insert edit row
    // -----------------------------
    var edit_row = $(
        "<tr />",
        {"class": "form-row inlined-model-edit",
         "id": "inlined-model-edit-" + inlined_model.id});
    fillEditRow(edit_row, inlined_model);
    edit_row.hide()
    $("#inlined-model-table tbody").append(edit_row);

    // Special hack for the "new" inlined_model: turn on autocomplete for this row
    if (inlined_model.id === "") {
        turnOnAttendeeAutocomplete(edit_row);
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
    console.log("Turning on autocomplete");

    // Hook in the autocomplete function
    edit_row.find("input.name").autocomplete({
        source: autoCompleteSourceHelper(getAutoCompleteUrl()),
        select: function(event, ui) {
            if (ui.item) {
                var inlined_model_id = ui.item.data.id;
                // Remove this row
                cancelInlinedModelEdit("");
                // Insert the inlined and make them immediately editable
                linkInlinedModel(inlined_model_id, true);
                // Don't replace the input value with the ui.item.value
                event.preventDefault();
            }
        }
    });
}

/*
  Create a link to the change form of an inlined model with the given ID
*/
function createProfileLink(inlined_model_id, existing_element, url_for_profile=null) {
    var link_to_profile = $("<a/>");
    link_to_profile.html(" &#x2139;");
    link_to_profile.attr("href", getExistingInlinedModelProfileUrl(inlined_model_id, url_for_profile));
    existing_element.append(link_to_profile);
}




/*
Wipe out a row and add the hidden inlined id input

Arguments:
 - row: jquery DOM element for this inlined <tr> row
 - inlined_model_id: the identifier for this linked model
*/
function resetRow(row, inlined_model_id) {
    row.empty();
    row.append($(
        "<input/>",
        {"type": "hidden",
         "class": "inlined-model-id",
         "value": inlined_model_id}));
}

/* Wipe out the static row and fill it with the appripriate elements

Arguments:
 - row: jquery DOM element for this inlined <tr> row
 - inlined: mapping representing this linked model's data
*/
function fillStaticRow(row, inlined_model) {
    var fields_config = getFieldsConfig();
    resetRow(row, inlined_model.id);

    fields_config.map(
        function(field) {
            var new_elt = fieldTypes[field.input_type].setupStatic(
                field,
                // The current representation for this field on the model
                inlined_model[field.form_name])
            if (field['form_name'] == 'name'){
                createProfileLink(inlined_model.id, new_elt);
            }
            else if (field['form_name'] == 'institution' && inlined_model.institution){
                // this doesn't work yet because I don't know how to set the URL correctly
                createProfileLink(inlined_model.institution.id, new_elt, "/swoptact/institution/");
            }
            td_wrap = $("<td/>");
            td_wrap.attr("data-form-name", field['form_name']);
            td_wrap.append(new_elt);
            row.append(td_wrap);
        });

    // Now append the buttons...
    row.append('<td><button type="submit" class="btn inlined-model-edit" name="_edit">✎ Edit</button> <button type="submit" class="btn inlined-model-unlink" name="_unlink">✘ Undo</button></td>');
}

/* Wipe out the edit row and fill it with the appripriate elements

Arguments:
 - row: jquery DOM element for this inlined <tr> row
 - inlined_model: mapping representing this linked model's data
*/
function fillEditRow(row, inlined_model) {
    var fields_config = getFieldsConfig();
    resetRow(row, inlined_model.id);

    fields_config.map(
        function(field) {
            var new_elt = fieldTypes[field.input_type].setupEdit(
                field,
                // The current representation for this field on the model
                inlined_model[field.form_name])
            td_wrap = $("<td/>");
            td_wrap.attr("data-form-name", field['form_name']);
            td_wrap.attr("data-input-type", field['input_type']);
            td_wrap.append(new_elt);
            if (field['form_name'] == 'name'){
                createProfileLink(inlined_model.id, td_wrap);
            }
            row.append(td_wrap);
        });

    // Now append the buttons...
    row.append('<td><button type="submit" class="btn inlined-model-save" name="_save">✓ Done</button> <button type="submit" class="btn inlined-model-cancel" name="_cancel">✗ Cancel</button></td>');
}

/* Wipe out the errors row and fill it with the appripriate elements

You might notice that this takes a `inlined_model_id' rather than a full
inlined object like the other "fill" methods... this is
intentional since this is called possibly in some places where that
full data is not available, and the other information is not used anyway.

Arguments:
 - row: jquery DOM element for this inlined <tr> row
 - inlined_model_id: the identifier for this linked model
 - errors: a list of strings representing errors that should be
   displayed.
*/
function fillErrorsRow(row, inlined_model_id, errors) {
    resetRow(row, inlined_model_id);

    var td = $('<td colspan="5" />');

    if (errors.length > 0) {
        td.append($("<p><i>Errors were found in the entry below...</i></p>"));
    }

    errors.forEach(function(error_msg) {
        warning_div = $('<div class="alert alert-danger" />');
        warning_div.text(error_msg);
        td.append(warning_div);
    });

    row.append(td);
}


/* Grab the initial list of linked items from the server & render */
function loadInitialAttendees() {
    var page_model_id = getPageModelId();
    var url = fillCurrentInlinesUrl(page_model_id);
    $.get(url, function (people_list) {
        for (i = 0; i < people_list.length; i++){
            insertInlinedModel(people_list[i]);
        }
    }, "json");
}


/* Add the inlined model on the backend and link on the frontend */
function linkInlinedModel(inlined_model_id, make_editable) {
    var url = fillLinkInlinedModelUrl(getPageModelId(), inlined_model_id);
    $.post(url, function (result) {
        $.get(fillExistingInlinedModelUrl(inlined_model_id),
              function (inlined_model) {
                  insertInlinedModel(inlined_model);
                  if (make_editable) {
                      makeInlinedModelEditable(inlined_model_id);
                  }
              }, 'json');
    }, "json");
}


/* Remove inlined model with INLINED_MODEL_ID from server and the UI. */
function unlinkInlinedModel(inlined_model_id){
    var removeRows = function () {
        getInlinedModelStaticRow(inlined_model_id).remove();
        getInlinedModelEditRow(inlined_model_id).remove();
        getInlinedModelErrorsRow(inlined_model_id).remove();
    }

    // An empty, pre-saved new inlined model.
    if (inlined_model_id == "") {
        removeRows();
        return false;
    }

    var page_model_id = getPageModelId();
    var target_url = fillLinkInlinedModelUrl(page_model_id, inlined_model_id);
    $.ajax({
        url: target_url,
        type: 'DELETE',
        success: removeRows});
}


/* Save all rows that are currently being edited

We have to rely on jquery telling us what's visible or not
since we don't have any other markers of what's in editing mode
*/
function saveAllEditing() {
    // Find all currently being edited rows and the inlined model thereof,
    // then save
    $("tr.inlined-model-edit:visible input.inlined-model-id").each(
        function(index) {
            saveInlinedModel(this.value, false);
        });
}


function addNewInlinedModel() {
    saveAllEditing();

    if (getInlinedModelEditRow("").length > 0) {
        // We already have an empty inlined model in progress
        return false;
    }

    // NOTE: Not all our code is really set up to handle
    // passing in a mostly empty object as an inlined object :\
    // This is a hack!
    // Seems to work tho
    insertInlinedModel({"id": ""});
    hideInlinedModelStaticRow("");
    showInlinedModelEditRow("");
}


/*
Helper function to find the correct rows and fill them using other functions,
after a inlined is updated
*/
function recreateRows(inlined_model){
    fillEditRow(getInlinedModelEditRow(inlined_model.id),
                inlined_model);
    fillErrorsRow(getInlinedModelErrorsRow(inlined_model.id),
                  inlined_model.id, []);
    fillStaticRow(getInlinedModelStaticRow(inlined_model.id),
                  inlined_model);
    hideInlinedModelEditRow(inlined_model.id);
    hideInlinedModelErrorsRow(inlined_model.id);
    showInlinedModelStaticRow(inlined_model.id);
}


// @@: Shouldn't this be getting the failure descriptions from the server?
//     That would be more consistent with how django form errors are displayed
//     and would be much more flexible
function handleJSONErrors(response, inlined_model_id){
    responseText = jQuery.parseJSON(response.responseText);
    var errors = responseText.form.errors;
    var error_array = [];
    if (errors.primary_phone){
        error_array.push("Sorry, but we can't interpret this phone number.  Please use (xxx) xxx-xxxx format. ");
    }
    if (errors.name){
        error_array.push("Sorry, but we can't interpret this name.  Please include at least one character.");
    }
    if (response.status == '400'){
        //interpret and display errors in a meaningful way
        fillErrorsRow(getInlinedModelErrorsRow(inlined_model_id), inlined_model_id, error_array);
        showInlinedModelErrorsRow(inlined_model_id);
    }
}

/* Save inlined model on server and update the UI

Arguments:
 - inlined_model_id: the identifier for this linked model
 - submit_flag: whether or not to submit the entire form
   NOTE: this is broken, see issue #105
*/
function saveInlinedModel(inlined_model_id, submit_flag) {
    // Get the row, extract the current mapping of fields to their data
    var row = getInlinedModelEditRow(inlined_model_id);
    var form_data = getDataForEditRow(row);

    // Handle if this is a new row, or an existing one
    //
    // @@: we shouldn't really have both "empty" and ""
    //   supported here.  We should simplify the code to just ""
    //   because otherwise we're going to end up with a lot of
    //   missed conditions and extra checks.
    if (inlined_model_id != "empty" && inlined_model_id != ""){
        $.get(fillExistingInlinedModelUrl(inlined_model_id),
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
                          handleJSONErrors(response, inlined_model_id);
                      },
                      success: function (response) {
                          recreateRows(response);
                          if (submit_flag){
                              $("div.change-content form").submit();
                          }
                      },
                      dataType: 'json'
                  });
              }, 'json');
    } else {
        $.ajax({
            url: getNewInlinedModelUrl(),
            data: JSON.stringify(form_data),
            type: 'POST',
            error: function (response, jqXHR) {
                handleJSONErrors(response, inlined_model_id);
            },
            success: function (response) {
                var url = fillLinkInlinedModelUrl(getPageModelId(), response.id);
                $.post(url, function (result) {
                    $.get(fillExistingInlinedModelUrl(response.id),
                          function (inlined_model) {
                              unlinkInlinedModel("");
                              insertInlinedModel(inlined_model);
                              if (submit_flag){
                                  $("div.change-content form").submit();
                              }
                          }, 'json');
                }, "json");
                
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
    $("#inlined-model-table thead tr").append($("<th>Actions</th>"));
}

/* Set up all the main widget callbacks */
function setupInlinedModelCallbacks() {
    //keep track of row(s) in the middle of being edited
    var rows_editing = [];
    $("#inlined-model-table").on(
        "click", "button.inlined-model-edit",
        function(event) {
            rows_editing.push(getInlinedModelIdForRow($(this)));
            event.preventDefault();
            makeInlinedModelEditable(getInlinedModelIdForRow($(this)));
        });

    $("#inlined-model-table").on(
        "click", "button.inlined-model-unlink",
        function(event) {
            event.preventDefault();
            unlinkInlinedModel(getInlinedModelIdForRow($(this)));
        });

    $("#inlined-model-table").on(
        "click", "button.inlined-model-cancel",
        function(event) {
            var index = rows_editing.indexOf(getInlinedModelIdForRow($(this)));
            if (index > -1){
                rows_editing.splice(index, 1);
            }
            event.preventDefault();
            cancelInlinedModelEdit(getInlinedModelIdForRow($(this)));
        });

    $("#inlined-model-table").on(
        "click", "button.inlined-model-save",
        function(event) {
            var index = rows_editing.indexOf(getInlinedModelIdForRow($(this)));
            if (index > -1){
                rows_editing.splice(index, 1);
            }
            event.preventDefault();
            saveInlinedModel(getInlinedModelIdForRow($(this)), false);
        });

    $("#add-new-inlined-model-btn").on(
        "click",
        function(event) {
            event.preventDefault();
            addNewInlinedModel();
            // addNewInlinedModel saves all open rows, so we empty the existing
            // array of rows being edited.
            rows_editing = [];
            // this case still needs to be handled correctly
            rows_editing.push('empty');
        });

    $("#inlined-model-table").on(
        "keypress",
        "tr.inlined-model-edit td input",
        function (event) {
            // 13 is enter key
            if (event.which == 13) {
                event.preventDefault();
                saveInlinedModel(getInlinedModelIdForRow($(this)), false);
            }
        });

    $("#multi_action_submit").on(
        "click",
        function (event) {
            if (rows_editing[0]){
                for (j = 0; j < rows_editing.length; j++) {
                    if (j == (rows_editing.length - 1) ) {
                        //for last value, pass the flag that says "and submit"
                        saveInlinedModel(rows_editing[j], true);
                    }
                    else{
                        saveInlinedModel(rows_editing[j], false);
                    }
                }
            }
            else{
                $("div.change-content form").submit();
            }
        });

    $(document).ready(function () {
        insertFormHeaders();
        insertFieldsetHeader();
        loadInitialAttendees();
    });
}

setupInlinedModelCallbacks();
