ALTER TABLE messages_messageacl ADD UNIQUE (`message_id`,`user_id`,`permission`);
ALTER TABLE users_userprofile ADD COLUMN `address` varchar(200);
ALTER TABLE users_userprofile ADD COLUMN `postcode` varchar(9);
ALTER TABLE users_userprofile ADD COLUMN `city` varchar(50);
ALTER TABLE users_userprofile ADD COLUMN `country` varchar(30);
ALTER TABLE users_userprofile ADD COLUMN `mobile` varchar(30);
ALTER TABLE users_userprofile ADD COLUMN `phone` varchar(30);
