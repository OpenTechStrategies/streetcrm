                           StreetCRM Design.
                           ================

*TODO (2015-11-19):* _This document is still incomplete_

# Searching

This app uses `django-watson` for searching.  To add a new model to the
basic search results:

1. Add a value for `search_fields` to the model's class in admin.py
2. Run `./manage.py buildwatson` to capture any existing instances of
the model.

Watson works by indexing objects in the `watson_searchentry` table.  Any
bizarre search  results are likely  a result of  inconsistencies between
that  table  and the  real  objects  in  the  database.  At  worst,  run
`truncate  watson_searchentry`  and  then `./manage.py  buildwatson`  to
bring  the search  results  back in  line  with the  real  state of  the
database.


# Interface
## Data Fields
Participants: first name, last name, phone number, address (street
number, street direction, street name, street type), email address
Events: name, date, location (site name and all address fields)

## Functionality
### Participants:
search, create, modify, delete, merge, link to event, unlink from event
### Events:
search, create, modify, delete, merge, link to participant, unlink from participant

# Database
## Participants
### id
### first name
### last name
### phone number
### street number
### street direction
### street name
### street type
### email address
## Events
### id
### name
### date
### site name
### street number
### street direction
### street name
### street type


## Participants_Events
### primary key...!
### participant id
### event id
### date linked
### date unlinked?

## Users and permissions

Making use of Django's builtins

## Contacts
## Events
