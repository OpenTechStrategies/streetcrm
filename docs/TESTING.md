# TESTING.md

## General functionality
- Objects can be saved and edited.
- Be sure to test saving users, in particular.  The "select-multiple"
there has been shown to be a special case. 
- Autocompletion works on regular form items and on AJAX-y form items.

## Inlined Models: Contacts and Sign-in Sheet

- Names autocomplete when adding new, but not when editing
- Institution names always autocomplete
- Phone numbers are validated and reformatted to (xxx) xxx-xxxx
- Invalid input displays an error (e.g., invalid phone number)
- Adding a contact or attendee who already exists in the db links to
  that Participant object and does not create a new one
- New institutions are marked with [NEW] and are created as new objects
- Editing data on these pages changes the underlying Participant object
- A new contact or attendee name that does not match any Participant
  object in the DB is created as a new Participant object
- Removing an inlined object removes the link between the page object
  and the inlined object, but does not remove the inlined object from
  the DB

###  Slow connections

- When a new person is added to an action on a slow connection (e.g. 50
  kb/s with 500ms RTT when testing on Chrome), only one copy of that
  person is created.
- PUT requests to create or link an institution to a person succeed
- PUT requests to update or add a phone number succeed
- Autocompletion on participant and institution names works
- Data entered while other requests are pending is not lost

## Permissions

- admin users can add and edit Contacts
- leader and staff users can neither add nor edit Contacts
- all users can add and edit Institutions, Participants, and Actions
- all users can add and edit Attendees of Actions
- admin users can create new Users
- admin and staff users can create and edit Tags
- leader users can neither create nor edit Tags


## Search

- Basic and advanced search should always show helptext when a search
  has no results.  They should not show this helptext before the user
  performs a search.  Specifically, test for no results with:
  - from the top search bar
  - from the basic search page
  - from the advanced search page
  - after a prior search with results
  - after a prior search with no results
