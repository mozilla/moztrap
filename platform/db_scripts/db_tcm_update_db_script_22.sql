USE tcm;

set foreign_key_checks =0;

DROP TABLE IF EXISTS Attachment;
CREATE TABLE `Attachment` (
  `attachmentId` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `description` text,
  `size` float DEFAULT NULL,
  `url` varchar(2048) DEFAULT NULL,
  `entityTypeId` int(11) NOT NULL,
  `entityId` int(11) NOT NULL,
  `attachmentTypeId` int(11) NOT NULL,
  `createdBy` int(11) NOT NULL,
  `createDate` datetime NOT NULL,
  `lastChangedBy` int(11) NOT NULL,
  `lastChangeDate` datetime NOT NULL,
  `version` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`attachmentId`),
  KEY `IDX_TypeAttachements` (`entityTypeId`,`entityId`,`attachmentTypeId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS AttachmentType;
CREATE TABLE `AttachmentType` (
  `attachmentTypeId` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`attachmentTypeId`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
insert into AttachmentType (attachmentTypeId) values (1);
insert into AttachmentType (attachmentTypeId) values (2);
insert into AttachmentType (attachmentTypeId) values (3);
insert into AttachmentType (attachmentTypeId) values (4);
insert into AttachmentType (attachmentTypeId) values (5);
insert into AttachmentType (attachmentTypeId) values (6);
insert into AttachmentType (attachmentTypeId) values (7);
insert into AttachmentType (attachmentTypeId) values (8);

DROP TABLE IF EXISTS AttachmentTypeLocale;
CREATE TABLE AttachmentTypeLocale ( attachmentTypeId INT NOT NULL AUTO_INCREMENT, name VARCHAR(50) NOT NULL, sortOrder INT DEFAULT '0' NOT NULL, localeCode VARCHAR(10) DEFAULT 'en_US' NOT NULL, PRIMARY KEY (attachmentTypeId, localeCode), CONSTRAINT FK_AttachmentType_ID FOREIGN KEY (attachmentTypeId) REFERENCES attachmenttype (attachmentTypeId) ON DELETE NO ACTION ON UPDATE NO ACTION ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
insert into AttachmentTypeLocale (attachmentTypeId, name, sortOrder, localeCode) values (1, 'Branding Image', 0, 'en_US');
insert into AttachmentTypeLocale (attachmentTypeId, name, sortOrder, localeCode) values (2, 'Design Document', 0, 'en_US');
insert into AttachmentTypeLocale (attachmentTypeId, name, sortOrder, localeCode) values (3, 'User Guide', 0, 'en_US');
insert into AttachmentTypeLocale (attachmentTypeId, name, sortOrder, localeCode) values (4, 'Requirements Document', 0, 'en_US');
insert into AttachmentTypeLocale (attachmentTypeId, name, sortOrder, localeCode) values (5, 'Known Issues', 0, 'en_US');
insert into AttachmentTypeLocale (attachmentTypeId, name, sortOrder, localeCode) values (6, 'Screen Capture', 0, 'en_US');
insert into AttachmentTypeLocale (attachmentTypeId, name, sortOrder, localeCode) values (7, 'NDA', 0, 'en_US');
insert into AttachmentTypeLocale (attachmentTypeId, name, sortOrder, localeCode) values (8, 'Unspecified', 0, 'en_US');

DROP TABLE IF EXISTS EntityType;
CREATE TABLE EntityType ( entityTypeId INT NOT NULL, PRIMARY KEY (entityTypeId) ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
insert into EntityType (entityTypeId) values (1);
insert into EntityType (entityTypeId) values (2);
insert into EntityType (entityTypeId) values (3);
insert into EntityType (entityTypeId) values (4);
insert into EntityType (entityTypeId) values (5);
insert into EntityType (entityTypeId) values (6);
insert into EntityType (entityTypeId) values (7);
insert into EntityType (entityTypeId) values (8);
insert into EntityType (entityTypeId) values (9);

DROP TABLE IF EXISTS EntityTypeLocale;
CREATE TABLE EntityTypeLocale ( entityTypeId INT NOT NULL AUTO_INCREMENT, name VARCHAR(50) NOT NULL, sortOrder INT DEFAULT '0' NOT NULL, localeCode VARCHAR(10) DEFAULT 'en_US' NOT NULL, PRIMARY KEY (entityTypeId, localeCode) ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
insert into EntityTypeLocale (entityTypeId, name, sortOrder, localeCode) values (1, 'Product', 0, 'en_US');
insert into EntityTypeLocale (entityTypeId, name, sortOrder, localeCode) values (2, 'TestCase', 0, 'en_US');
insert into EntityTypeLocale (entityTypeId, name, sortOrder, localeCode) values (3, 'TestSuite', 0, 'en_US');
insert into EntityTypeLocale (entityTypeId, name, sortOrder, localeCode) values (4, 'TestPlan', 0, 'en_US');
insert into EntityTypeLocale (entityTypeId, name, sortOrder, localeCode) values (5, 'TestCycle', 0, 'en_US');
insert into EntityTypeLocale (entityTypeId, name, sortOrder, localeCode) values (6, 'TestRun', 0, 'en_US');
insert into EntityTypeLocale (entityTypeId, name, sortOrder, localeCode) values (7, 'TestResult', 0, 'en_US');
insert into EntityTypeLocale (entityTypeId, name, sortOrder, localeCode) values (8, 'User', 0, 'en_US');
insert into EntityTypeLocale (entityTypeId, name, sortOrder, localeCode) values (9, 'Company', 0, 'en_US');

-- new permissions
insert into Permission (permissionCode, name, assignable) values ('PERMISSION_ATTACHMENT_ADD', '', '1');
insert into Permission (permissionCode, name, assignable) values ('PERMISSION_ATTACHMENT_VIEW', '', '1');
insert into Permission (permissionCode, name, assignable) values ('PERMISSION_ATTACHMENT_EDIT', '', '1');

-- update admin permissions
insert into RolePermission (permissionId, accessRoleId, createdBy, createDate, lastChangedBy, lastChangeDate) 
select permissionId, 1, 1, current_timestamp, 1, current_timestamp
from Permission p
where not exists 
(
select 1 from RolePermission where accessRoleId = 1 and permissionId = p.permissionId
)
and permissionId > 0;

