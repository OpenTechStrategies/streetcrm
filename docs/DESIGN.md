                           SWOPtact Design.
                           ================

*TODO (2015-11-19):* _This document is still incomplete_

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
