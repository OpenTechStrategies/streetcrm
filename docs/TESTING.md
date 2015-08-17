# TESTING.md

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
- 