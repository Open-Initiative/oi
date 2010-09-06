BEGIN;
CREATE TABLE `users_userprofile_contacts` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `from_userprofile_id` integer NOT NULL,
    `to_userprofile_id` integer NOT NULL,
    UNIQUE (`from_userprofile_id`, `to_userprofile_id`)
)
;
ALTER TABLE `users_userprofile_contacts` ADD CONSTRAINT `from_userprofile_id_refs_id_7ee09a1e` FOREIGN KEY (`from_userprofile_id`) REFERENCES `users_userprofile` (`id`);
ALTER TABLE `users_userprofile_contacts` ADD CONSTRAINT `to_userprofile_id_refs_id_7ee09a1e` FOREIGN KEY (`to_userprofile_id`) REFERENCES `users_userprofile` (`id`);
ALTER TABLE `projects_project` ADD COLUMN `progress` double precision;
COMMIT;
