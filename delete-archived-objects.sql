/* 
 * Remove archived objects from an instance of StreetCRM.  Tables don't
 * have cascade, so any foreign keys must be deleted first. 
*/ 

DELETE FROM "streetcrm_institution_contacts" WHERE "institution_id" IN (SELECT "id" FROM "streetcrm_institution" WHERE "archived" IS NOT NULL);
DELETE FROM "streetcrm_institution_contacts" WHERE "participant_id" IN (SELECT "id" FROM "streetcrm_participant" WHERE "archived" IS NOT NULL);
DELETE FROM "streetcrm_event_participants" WHERE "participant_id" IN (SELECT "id" FROM "streetcrm_participant" WHERE "archived" IS NOT NULL);
DELETE FROM "streetcrm_event_participants" WHERE "event_id" IN (SELECT "id" FROM "streetcrm_event" WHERE "archived" IS NOT NULL);
DELETE FROM "streetcrm_event_tags" WHERE "event_id" IN (SELECT "id" FROM "streetcrm_event" WHERE "archived" IS NOT NULL);
DELETE FROM "streetcrm_event_tags" WHERE "tag_id" IN (SELECT "id" FROM "streetcrm_tag" WHERE "archived" IS NOT NULL);
DELETE FROM "streetcrm_institution_tags" WHERE "institution_id" IN (SELECT "id" FROM "streetcrm_institution" WHERE "archived" IS NOT NULL); 
DELETE FROM "streetcrm_institution_tags" WHERE "tag_id" IN (SELECT "id" FROM "streetcrm_tag" WHERE "archived" IS NOT NULL); 

UPDATE "streetcrm_event" SET "organizer_id"=NULL WHERE "organizer_id" IN (SELECT "id" FROM "streetcrm_participant" WHERE "archived" IS NOT NULL); 
UPDATE "streetcrm_event" SET "secondary_organizer_id"=NULL WHERE "secondary_organizer_id" IN (SELECT "id" FROM "streetcrm_participant" WHERE "archived" IS NOT NULL);
UPDATE "streetcrm_participant" set "institution_id"=NULL WHERE "institution_id" IN (SELECT "id" FROM "streetcrm_institution" WHERE "archived" IS NOT NULL);

DELETE FROM "streetcrm_event" WHERE "archived" IS NOT NULL;
DELETE FROM "streetcrm_tag" WHERE "archived" IS NOT NULL; 
DELETE FROM "streetcrm_institution" WHERE "archived" IS NOT NULL; 
DELETE FROM "streetcrm_participant" WHERE "archived" IS NOT NULL; 


