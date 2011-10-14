
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS TestCycleUser;
DROP TABLE IF EXISTS TestCycleUserRole;


DROP  TABLE IF EXISTS `Team`;
CREATE TABLE `Team` (
  `teamId` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL COMMENT 'Name of the team.',
  `description` text COMMENT 'Detailed description.',
  `companyId` int(11) NOT NULL,
  `createdBy` int(11) NOT NULL,
  `createDate` datetime NOT NULL,
  `lastChangedBy` int(11) NOT NULL,
  `lastChangeDate` datetime NOT NULL,
  `version` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`teamId`),
  KEY `fk_Team_Company` (`companyId`),
  CONSTRAINT `fk_Team_Company` FOREIGN KEY (`companyId`) REFERENCES `Company` (`companyId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

DROP  TABLE IF EXISTS `TeamUser`;
CREATE TABLE `TeamUser` (
  `teamUserId` int(11) NOT NULL AUTO_INCREMENT,
  `teamId` int(11) NOT NULL,
  `userId` int(11) NOT NULL,
  `createdBy` int(11) NOT NULL,
  `createDate` datetime NOT NULL,
  `lastChangedBy` int(11) NOT NULL,
  `lastChangeDate` datetime NOT NULL,
  PRIMARY KEY (teamUserId),
  CONSTRAINT `fk_TeamUser_Team` FOREIGN KEY (`teamId`) REFERENCES `Team` (`teamId`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_TeamUser_User` FOREIGN KEY (`userId`) REFERENCES `User` (`userId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Team member.';

DROP  TABLE IF EXISTS `TeamUserRole`;
CREATE TABLE `TeamUserRole` (
  `teamUserRoleId` int(11) NOT NULL AUTO_INCREMENT,
  `teamId` int(11) NOT NULL,
  `userId` int(11) NOT NULL,
  `accessRoleId` int(11) NOT NULL,
  `createdBy` int(11) NOT NULL,
  `createDate` datetime NOT NULL,
  `lastChangedBy` int(11) NOT NULL,
  `lastChangeDate` datetime NOT NULL,
  PRIMARY KEY (teamUserRoleId),
  CONSTRAINT `fk_TeamUserRole_Role` FOREIGN KEY (`accessRoleId`) REFERENCES `AccessRole` (`accessRoleId`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_TeamUserRole_Team` FOREIGN KEY (`teamId`) REFERENCES `Team` (`teamId`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_TeamUserRole_User` FOREIGN KEY (`userId`) REFERENCES `User` (`userId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Team member role.';

ALTER TABLE Product ADD (teamId INT);
ALTER TABLE Product ADD CONSTRAINT fk_Product_EnvironmentProfile FOREIGN KEY (environmentProfileId) REFERENCES EnvironmentProfile (environmentProfileId) ON
DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE Product ADD CONSTRAINT fk_Product_Team FOREIGN KEY (teamId) REFERENCES Team (teamId) ON
DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE TestCycle ADD (teamId INT);
ALTER TABLE TestCycle ADD CONSTRAINT fk_TestCycle_EnvironmentProfile FOREIGN KEY (environmentProfileId) REFERENCES EnvironmentProfile (environmentProfileId) ON
DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE TestCycle ADD CONSTRAINT fk_TestCycle_Team FOREIGN KEY (teamId) REFERENCES Team (teamId) ON
DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE TestRun ADD (teamId INT);
ALTER TABLE TestRun ADD CONSTRAINT fk_TestRun_EnvironmentProfile FOREIGN KEY (environmentProfileId) REFERENCES EnvironmentProfile (environmentProfileId) ON
DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE TestRun ADD CONSTRAINT fk_TestRun_Team FOREIGN KEY (teamId) REFERENCES Team (teamId) ON
DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE TestRun ADD (autoAssignToTeam TINYINT(1) DEFAULT '0' NOT NULL);

ALTER TABLE TestRunTestCase ADD CONSTRAINT fk_TestRunTestCase_EnvironmentProfile FOREIGN KEY (environmentProfileId) REFERENCES EnvironmentProfile (environmentProfileId) ON
DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE TestRunTestCaseAssignment ADD CONSTRAINT fk_TestRunTestCaseAssignment_EnvironmentProfile FOREIGN KEY (environmentProfileId) REFERENCES EnvironmentProfile (environmentProfileId) ON
DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE TestRunResult ADD CONSTRAINT fk_TestRunResult_EnvironmentGroup FOREIGN KEY (environmentGroupId) REFERENCES EnvironmentGroup (environmentGroupId) ON
DELETE NO ACTION ON UPDATE NO ACTION;

-- new permissions
insert into Permission (permissionCode, name, assignable) values ('PERMISSION_TEAM_VIEW', '', '1');
insert into Permission (permissionCode, name, assignable) values ('PERMISSION_TEAM_EDIT', '', '1');



