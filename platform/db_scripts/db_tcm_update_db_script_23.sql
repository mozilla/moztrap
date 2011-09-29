USE tcm;

set foreign_key_checks =0;

ALTER TABLE
    TestCycle ADD (featured TINYINT(1) DEFAULT '0' NOT NULL);

ALTER TABLE
    TestRun ADD (featured TINYINT(1) DEFAULT '0' NOT NULL);

DROP TABLE
    `TestRunExternalBug`;
    
DROP TABLE IF EXISTS EntityExternalBug;
CREATE TABLE `EntityExternalBug` (
  `entityExternalBugId` int(11) NOT NULL AUTO_INCREMENT,
  `externalIdentifier` varchar(250) NOT NULL,
  `url` varchar(2048) DEFAULT NULL,
  `entityTypeId` int(11) NOT NULL,
  `entityId` int(11) NOT NULL,
  `createdBy` int(11) NOT NULL,
  `createDate` datetime NOT NULL,
  `lastChangedBy` int(11) NOT NULL,
  `lastChangeDate` datetime NOT NULL,
  `version` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`entityExternalBugId`),
  KEY `IDX_Enity_Bugs` (`entityTypeId`,`entityId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- new permissions
insert into Permission (permissionCode, name, assignable) values ('PERMISSION_FEATURED_LIST_EDIT', '', '1');
insert into Permission (permissionCode, name, assignable) values ('PERMISSION_EXTERNAL_BUG_VIEW', '', '1');
insert into Permission (permissionCode, name, assignable) values ('PERMISSION_EXTERNAL_BUG_EDIT', '', '1');

-- update admin permissions
insert into RolePermission (permissionId, accessRoleId, createdBy, createDate, lastChangedBy, lastChangeDate) 
select permissionId, 1, 1, current_timestamp, 1, current_timestamp
from Permission p
where not exists 
(
select 1 from RolePermission where accessRoleId = 1 and permissionId = p.permissionId
)
and permissionId > 0;

