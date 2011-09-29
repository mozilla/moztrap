ALTER TABLE `User` ADD (screenName VARCHAR(12) NOT NULL);

UPDATE `User`
set screenName = concat('userName', userId);