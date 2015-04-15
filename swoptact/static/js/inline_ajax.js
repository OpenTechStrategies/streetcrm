/*
Eventually, this page should be able to do the following things:
(1) find the relevant participants for a given event and (2) display 
information about each of them, then (3) offer textboxes populated by values
from that object onclick of an edit button and (4) save changes made via those
text boxes by sending the new information as a JSON object to an endpoint
elsewhere.
It should also (5) remove a relationship between a person and an event, (6) add
an entirely new person (really the same as (4)), and (7) search for and (8) link
an existing person to this event.

Currently it does only number two (2), of the above.
*/

/*
Very basic function to get the JSON object from one of the API URL's.
*/
function Get(yourUrl){
    var Httpreq = new XMLHttpRequest(); // a new request
    Httpreq.open("GET",yourUrl,false);
    Httpreq.send(null);
    var model = Httpreq.responseText;
    var obj = JSON.parse(model)
    return obj;
    }

/*
Takes a URL in order to call the function above and inserts the resultant JSON
object as a table row.
*/
function displayPerson(URL){
    var person = Get(URL);
    var target_table = document.getElementById('attendees_table');
    var row = target_table.insertRow(1);
    var person_info = [person.first_name, person.last_name,
                            person.phone_number, person.institution.name];
    for	(index = 0; index < person_info.length; index++) {
        var insert_cell = row.insertCell(index);
        insert_cell.innerHTML = person_info[index];
    }
}

// example
displayPerson('/api/participants/14/');
