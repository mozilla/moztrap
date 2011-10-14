

ALTER TABLE TestCycle MODIFY COLUMN environmentProfileId INT;

ALTER TABLE TestCase ADD   `createdBy` int(11) NOT NULL;
ALTER TABLE TestCase ADD   `createDate` datetime NOT NULL;
ALTER TABLE TestCase ADD   `lastChangedBy` int(11) NOT NULL;
ALTER TABLE TestCase ADD   `lastChangeDate` datetime NOT NULL;

update TestCase 
set createdBy = 1, 
createDate = CURRENT_TIMESTAMP, 
lastChangedBy = 1, 
lastChangeDate  = CURRENT_TIMESTAMP;