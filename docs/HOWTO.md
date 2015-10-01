# How To Use Engagemint #

### Log in
  - An admin user will need to create a username and password for you.  Use these to log in.
-  "Site Administration" page
   - Clicking on either the SWOP logo or "Contacts" title will return you to this list of the kinds of elements that the logged-in user has permission to edit.
   - The purple banner will show you where you are in the site at all times.  Right now it shows "Home," and you can always click on the home (or the logo) to get out of an inner page.
   - Search (see "Miscellaneous" for details).  If you know that you're looking for a specific person, institution, or action, type the name in the search bar.
   - To log out or change the password (if the logged-in user has permission to change their password), click the three horizontal lines at the top right, next to the "welcome, (user)" text.  You need to click directly on the text in that dropdown menu, not elsewhere in the highlighted row.
   - The list of elements under "site administration" shows what kinds of things the logged-in user has permission to edit.  We'll go through those below.
   - See more about the missing data report in "Miscellaneous," below.
   
### Click on "Actions"   
-  You'll see a list of actions.
   - This list can be filtered by tag and by whether or not the action has been archived.  These filteres are available on the right side of the center panel.
   - You can also sort the list by the column headers.  When you sort by a header, an arrow will appear to show which direction the list is being sorted, and an X will appear that allows you to undo the sorting if you want.  You can sort by multiple columns, so if you want to sort by one and then by another (instead of combining them), make sure you click the "X" to get rid of the first sort.
- Click on "Create new action"
  - Most of the fields are straightforward.  Some are filled by autocompletion: organizer, second organizer, tags, connected action.  To fill those in, start typing and then select something from the autocompletion list that appears.  If the organizer (or secondary organizer) you need doesn't appear in the list, just type his or her name.  Similarly, if you don't see the connected action that you need, just type its name and it will be created when you save the page.  However, new tags _cannot_ be created on this page.  You can only use a tag if it appears via autocompletion.
  - Click on the calendar icon to add date of action.
  - Note the message at the bottom that reminds you that you need to save before adding attendees.
  - Click "Save Changes."
    - explain what save changes does
  - To leave the page and return to the list of actions, click on "Actions" in the breadcrumb in the purple bar at the top of the page.  Or, click on the logo and then click on "Actions" again from the front page.
- Edit an action.  Click on the action you just created.
  - The organizers and connected action now show up as static text with a pencil.  Clicking the pencil will remove them and return an empty text box.  Click the pencil to change those fields.
  - Scroll down to the "Attendees" section.
    - Click "Add New" to add the first attendee.  Use autocompletion to find the names from the sign-in sheet.  If the name doesn't show up in the autocompletion list, then just keep typing it.  Tab to the next column to enter the institution.
    - Similarly, the institution should be entered from the autocompletion selections, but if it doesn't appear, type the name of the institution.  The word "[NEW]" will appear next to the institution name if it doesn't appear already in the database.  Tabbing away or entering will save that new institution and link it to the participant.
    - Tab or click over to add the phone number.  The phone number can be accepted in a few different formats, but it must be a valid phone number and must have the area code.  If you enter the full number and are still getting an error, check the format and then check the number.  If the area code is not valid then the phone number will error and not save.
    - The final column is a red "x" that removes the attendee from the sign-in sheet.
  - You'll see that each row has "i"s that link to the participant page and institution page.  Click either of those (they'll each open in a new tab) to see and edit more information about the person and the institution (respectively).
  - Clicking, tabbing, or clicking enter from each cell in this table will auto save it.
  - If you see a typo in an attendee name that has already been entered, editing it from the attendee list will edit it everywhere in the database.  Therefore, if you realize that someone is on the attendee list who should not be, click the red "x" to remove the row instead of editing the name.  Editing the name will not add a different person -- it will change the name of that person, which might mean that the new name is associated with the wrong institution, phone number, title, and other information.
-  list of institutions
   - (can't filter by tags?)
   - filter by archived status
-  add an institution
   - note autocompletion on tags
   - member y/n checkbox
   - save to add contacts
-  edit an institution
   - can add multiple tags (so the input remains to the right of the existing tags)
   - click pencil to remove tag
   - add contact with "add new"
   - limited to 4 contacts
   - click "i" to see the full participant page in a new tab
   - edit title here
   - same possible phone number errors
-  list of participants
   - sort by column headers
   - filter by archived
-  add a participant
   - institution is required
   - save changes v. done
   - action history will be empty until they are listed as attending an action
   - phone formatting
-  edit participant
   - same, but with links to the action if any are listed
   - action list is limited to more recent 5 actions
- list of tags
  - sort by column headers
  - filter by archived
- create a tag
  - name is short and to the point (limited to 25 chars)
  - description can give more details
- edit tag
  - see above
- list of activity log
  - shows recent changes ordered by date/time of change
  - not sortable
- create activity log
  - One is automatically created whenever anything is changed.  I don't think it's a great idea to create them manually.
- edit activity log
  - Again, these are created automatically, so it's probably not good to make manual edits to them.  However, you could do so to store extra information about a change.
  - Note that an edit to an activity log is itself stored in the log
  - Don't change the "object_repr" field, the content type, or the object id.

# User Administration #

- list of users
  - sort by column headers
  - filter by active/inactive
  - filter by group membership (note that people can and will be in multiple groups)
- create a user
  - unique username
  - passwords can be changed after the fact
  - click "done" and then choose what group(s) the user should be in.  Do not grant superuser status.  Don't edit the dates.
  - setting user active or inactive (with checkbox) allows them to log in or not
- list of groups
  - We set these groups up, but others could be made with a different combination of existing permissions.
  - the dropdown is used to delete groups, if necessary (but really, please don't)
- create a group
- edit a group

# Miscellaneous #

- add a tag to an institution or action
  - see edit institution and edit action sections
-  add a contact to an institution
   - see edit institution section
-  add an attendee to an event
   - see "edit action" section
- missing data report
- search
- advanced search (once it comes)